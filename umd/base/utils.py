import os
import os.path
import sys

import fabric
from fabric import colors

from umd import api
from umd import config
from umd import system
from umd import utils


def qcstep_request(f):
    """Decorator method that handles on-demand QC step executions."""
    def _request(self, *args, **kwargs):
        step_methods = []
        if "qc_step" in kwargs.keys():
            for step in utils.to_list(kwargs["qc_step"]):
                try:
                    method = getattr(self, step.lower())
                    step_methods.append(method)
                except AttributeError:
                    api.info("Ignoring QC step '%s': not defined." % step)
                    continue
        return f(self, step_methods, *args, **kwargs)
    return _request


def get_qc_envvars():
    """Returns a dict with the bash environment variables found in conf."""
    return dict([(k.split("qcenv_")[1], v)
                 for k, v in config.CFG.items() if k.startswith("qcenv")])


class QCStep(object):
    """Manages all the common functions that are used in a QC step."""
    def __init__(self, id, description, logfile):
        self.id = id
        self.description = description
        self.logfile = os.path.join(config.CFG["log_path"], logfile)
        self.logs = []

        self._print_header()
        self._remove_last_logfile()

    def _print_header(self):
        """Prints a QC header with the id and description."""
        print("[[%s: %s]]" % (colors.blue(self.id),
                              colors.blue(self.description)))

    def _remove_last_logfile(self):
        for stdtype in ("stdout", "stderr"):
            _fname = '.'.join([self.logfile, stdtype])
            if os.path.exists(_fname):
                os.remove(_fname)

    def print_result(self, level, msg, do_abort=False):
        """Prints the final result of the current QC step."""
        level_color = {
            "FAIL": colors.red,
            "NA": colors.green,
            "OK": colors.green,
            "WARNING": colors.yellow,
        }

        msg = "[%s] %s." % (level_color[level](level), msg)
        if do_abort:
            msg = ' '.join([msg, utils.format_error_msg(self.logs)])
            print(msg)
            sys.exit(1)
        else:
            print(msg)

    def runcmd(self,
               cmd,
               chdir=None,
               fail_check=True,
               stop_on_error=True,
               log_to_file=True,
               get_error_msg=False,
               stderr_to_stdout=False):
        logfile = None
        if log_to_file:
            logfile = self.logfile

        r = utils.runcmd(cmd,
                         chdir=chdir,
                         fail_check=fail_check,
                         stop_on_error=stop_on_error,
                         logfile=logfile,
                         get_error_msg=get_error_msg,
                         stderr_to_stdout=stderr_to_stdout)
        try:
            self.logs = r.logfile
        except AttributeError:
            pass

        return r


class OwnCACert(object):
    """Host certificate class."""
    def __init__(self, subject):
        self.subject = subject


class OwnCA(object):
    """Creates a Certification Authority to sign host certificates."""
    def __init__(self,
                 domain_comp_country,
                 domain_comp,
                 common_name):
        self.domain_comp_country = domain_comp_country
        self.domain_comp = domain_comp
        self.common_name = common_name
        self.workspace = os.path.join("/root/", common_name)
        self.subject = "/DC=%s/DC=%s/CN=%s" % (self.domain_comp_country,
                                               self.domain_comp,
                                               self.common_name)

    def create(self, trusted_ca_dir=None):
        """Creates the CA public and private key.

                trusted_ca_dir: if set, it will copy the CA public key and the
                                signing policy file under the trusted CA
                                directory.
        """
        utils.runcmd("mkdir -p %s" % self.workspace)
        with fabric.context_managers.lcd(self.workspace):
            subject = self.subject
            utils.runcmd(("openssl req -x509 -nodes -days 1 -newkey rsa:2048 "
                          "-out ca.pem -outform PEM -keyout ca.key -subj "
                          "'%s'" % subject))
            if trusted_ca_dir:
                hash = utils.runcmd("openssl x509 -noout -hash -in ca.pem")
                utils.runcmd("cp ca.pem %s"
                             % os.path.join(trusted_ca_dir,
                                            '.'.join([hash, '0'])))
                with open(os.path.join(
                    trusted_ca_dir,
                    '.'.join([hash, "signing_policy"])), 'w') as f:
                    f.writelines([
                        "access_id_CA\tX509\t'%s'\n" % subject,
                        "pos_rights\tglobus\tCA:sign\n",
                        "cond_subjects\tglobus\t'\"/DC=%s/DC=%s/*\"'\n"
                        % (self.domain_comp_country,
                           self.domain_comp)])

    def issue_cert(self,
                   hostname=system.fqdn,
                   hash="1024",
                   key_prv=None,
                   key_pub=None):
        """Issues a cert.

                hostname: CN value.
                key_prv: Alternate path to store the certificate's private key.
                key_pub: Alternate path to store the certificate's public key.
        """
        with fabric.context_managers.lcd(self.workspace):
            subject = "/DC=%s/DC=%s/CN=%s" % (self.domain_comp_country,
                                              self.domain_comp,
                                              hostname)
            utils.runcmd(("openssl req -newkey rsa:%s -nodes -sha1 -keyout "
                          "cert.key -keyform PEM -out cert.req -outform PEM "
                          "-subj '%s'"
                          % (hash, subject)))
            utils.runcmd(("openssl x509 -req -in cert.req -CA ca.pem -CAkey "
                          "ca.key -CAcreateserial -out cert.crt -days 1"))

            if key_prv:
                utils.runcmd("cp cert.key %s" % key_prv)
                api.info("Private key stored in '%s'." % key_prv)
            if key_pub:
                utils.runcmd("cp cert.crt %s" % key_pub)
                api.info("Public key stored in '%s'." % key_pub)

        return OwnCACert(subject)

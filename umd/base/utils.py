import os
import os.path

from fabric.api import abort
from fabric.colors import blue
from fabric.colors import green
from fabric.colors import red
from fabric.colors import yellow
from fabric.context_managers import lcd

from umd.api import info
from umd.config import CFG
from umd import system
from umd.utils import format_error_msg
from umd.utils import runcmd
from umd.utils import to_list


def qcstep_request(f):
    """Decorator method that handles on-demand QC step executions."""
    def _request(self, *args, **kwargs):
        step_methods = []
        if "qc_step" in kwargs.keys():
            for step in to_list(kwargs["qc_step"]):
                try:
                    method = getattr(self, step.lower())
                    step_methods.append(method)
                except AttributeError:
                    info("Ignoring QC step '%s': not defined." % step)
                    continue
        if step_methods:
            return f(self, step_methods, *args, **kwargs)
    return _request


def get_qc_envvars():
    """Returns a dictionary with the bash environment variables found
       in configuration.
    """
    return dict([(k.split("qcenv_")[1], v)
                  for k, v in CFG.items() if k.startswith("qcenv")])


class QCStep(object):
    """Manages all the common functions that are used in a QC step."""
    def __init__(self, id, description, logfile):
        self.id = id
        self.description = description
        self.logfile = logfile
        self.logs = []

        self._print_header()
        self._remove_last_logfile()

    def _print_header(self):
        """Prints a QC header with the id and description."""
        print("[[%s: %s]]" % (blue(self.id),
                              blue(self.description)))

    def _remove_last_logfile(self):
        for stdtype in ("stdout", "stderr"):
            _fname = '.'.join([self.logfile, stdtype])
            if os.path.exists(_fname):
                os.remove(_fname)

    def print_result(self, level, msg, do_abort=False):
        """Prints the final result of the current QC step."""
        level_color = {
            "FAIL": red,
            "NA": green,
            "OK": green,
            "WARNING": yellow,
        }

        msg = "[%s] %s." % (level_color[level](level), msg)
        if do_abort:
            msg = ' '.join([msg, format_error_msg(self.logs)])
            abort(msg)
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

        r = runcmd(cmd,
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

    def create(self, trusted_ca_dir=None):
        """Creates the CA public and private key.

                trusted_ca_dir: if set, it will copy the CA public key and the
                                signing policy file under the trusted CA
                                directory.
        """
        runcmd("mkdir -p %s" % self.workspace)
        with lcd(self.workspace):
            subject = "/DC=%s/DC=%s/CN=%s" % (self.domain_comp_country,
                                              self.domain_comp,
                                              self.common_name)
            runcmd(("openssl req -x509 -nodes -days 1 -newkey rsa:2048 "
                    "-out ca.pem -outform PEM -keyout ca.key -subj "
                    "'%s'" % subject))
            if trusted_ca_dir:
                hash = runcmd("openssl x509 -noout -hash -in ca.pem")
                runcmd("cp ca.pem %s" % os.path.join(trusted_ca_dir,
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
        with lcd(self.workspace):
            runcmd(("openssl req -newkey rsa:%s -nodes -sha1 -keyout "
                    "cert.key -keyform PEM -out cert.req -outform PEM "
                    "-subj '/DC=%s/DC=%s/CN=%s'" % (hash,
                                                    self.domain_comp_country,
                                                    self.domain_comp,
                                                    hostname)))
            runcmd(("openssl x509 -req -in cert.req -CA ca.pem -CAkey ca.key "
                    "-CAcreateserial -out cert.crt -days 1"))

            if key_prv:
                runcmd("cp cert.key %s" % key_prv)
                info("Private key stored in '%s'." % key_prv)
            if key_pub:
                runcmd("cp cert.crt %s" % key_pub)
                info("Public key stored in '%s'." % key_pub)

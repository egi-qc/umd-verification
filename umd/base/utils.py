import functools
import os
import os.path

import fabric
from fabric import colors

from umd import api
from umd import config
from umd import system
from umd import utils

openssl_cnf = """
[ ca ]
default_ca = myca

[ myca ]
dir = ./
new_certs_dir = $dir
unique_subject = no
certificate = $dir/ca.pem
database = $dir/index.txt
private_key = $dir/ca.key
crlnumber = $dir/crlnumber
serial = $dir/certserial
default_days = 730
default_md = sha1
default_crl_days = 730
"""


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


def qcstep(id, description):
    """Decorator method that prints QC step header."""
    def _qcstep(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            print("[[%s: %s]]" % (colors.blue(id),
                                  colors.blue(description)))
            return f(*args, **kwargs)
        return wrapper
    return _qcstep


def get_qc_envvars():
    """Returns a dict with the bash environment variables found in conf."""
    return dict([(k.split("qcenv_")[1], v)
                 for k, v in config.CFG.items() if k.startswith("qcenv")])


def get_subject(hostcert):
    return utils.runcmd(("openssl x509 -in %s -noout "
                         "-subject" % hostcert)).split()[1]


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
                # CA cert (.0)
                ca_dest = os.path.join(trusted_ca_dir, '.'.join([hash, '0']))
                utils.runcmd("cp ca.pem %s" % ca_dest)
                # CRL cert (.r0)
                # FIXME(orviz) check why absolute path is needed here
                with open(os.path.join(self.workspace,
                                       "openssl.cnf"), 'w') as f:
                    f.write(openssl_cnf)
                utils.runcmd("echo \"01\" > crlnumber")
                utils.runcmd("touch index.txt")
                utils.runcmd(("openssl ca -config openssl.cnf -gencrl "
                              "-keyfile ca.key -cert ca.pem -out crl.pem"))
                crl_dest = os.path.join(trusted_ca_dir, '.'.join([hash, 'r0']))
                utils.runcmd("cp crl.pem %s" % crl_dest)
                # signing_policy
                signing_policy_dest = os.path.join(
                    trusted_ca_dir,
                    '.'.join([hash, "signing_policy"]))
                with open(signing_policy_dest, 'w') as f:
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
                utils.runcmd("chmod 600 cert.key")
                utils.runcmd("cp cert.key %s" % key_prv)
                api.info("Private key stored in '%s' (with 600 perms)."
                         % key_prv)
            if key_pub:
                utils.runcmd("cp cert.crt %s" % key_pub)
                api.info("Public key stored in '%s'." % key_pub)

        return OwnCACert(subject)

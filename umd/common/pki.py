import os.path

import fabric
from fabric import operations as fabric_ops

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

[req]
distinguished_name = req_dn
req_extensions = v3_req

[req_dn]

[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
IP.1 = 127.0.0.1
"""


def certify():
    """Create host certificate and private key."""
    cert_path = "/etc/grid-security/hostcert.pem"
    key_path = "/etc/grid-security/hostkey.pem"
    do_cert = True
    if os.path.isfile(cert_path) and os.path.isfile(key_path):
        r = fabric_ops.prompt(("Certificate already exists under "
                               "'/etc/grid-security'. Do you want to "
                               "overwrite them? (y/N)"))
        if r.lower() == "y":
            api.info("Overwriting already existant certificate")
        else:
            do_cert = False
            api.info("Using already existant certificate")

    cert_for_subject = None
    if do_cert:
        hostcert = config.CFG.get("hostcert", None)
        hostkey = config.CFG.get("hostkey", None)
        if hostkey and hostcert:
            api.info("Using provided host certificates")
            utils.runcmd("cp %s %s" % (hostkey, key_path))
            utils.runcmd("chmod 600 %s" % key_path)
            utils.runcmd("cp %s %s" % (hostcert, cert_path))
            cert_for_subject = hostcert
        else:
            api.info("Generating own certificates")
            config.CFG["ca"] = OwnCA(
                domain_comp_country="es",
                domain_comp="UMDverification",
                common_name="UMDVerificationOwnCA")
            config.CFG["ca"].create(
                trusted_ca_dir="/etc/grid-security/certificates")
            config.CFG["cert"] = config.CFG["ca"].issue_cert(
                hash="2048",
                key_prv=key_path,
                key_pub=cert_path)
    else:
        cert_for_subject = cert_path

    if cert_for_subject:
        subject = get_subject(cert_for_subject)
        config.CFG["cert"] = OwnCACert(subject)

def get_subject(hostcert):
    return utils.runcmd(("openssl x509 -in %s -noout "
                         "-subject" % hostcert)).split()[1]


def trust_ca(ca_location):
    """Add the given CA to the system's CA trust database."""
    if system.distname == "ubuntu":
        trust_dir = "/usr/share/ca-certificates/"
        trust_cmd = "update-ca-certificates"
    elif system.distname == "centos":
        trust_dir = "/etc/pki/ca-trust/source/anchors/"
        trust_cmd = "update-ca-trust"

    ca_location_basename = os.path.basename(ca_location)
    ca_location_basename_crt = '.'.join([
        ca_location_basename.split('.')[0], "crt"])
    utils.runcmd("cp %s %s" % (
        ca_location,
        os.path.join(trust_dir, ca_location_basename_crt)))
    utils.runcmd("echo '%s' >> /etc/ca-certificates.conf"
                 % ca_location_basename_crt)
    r = utils.runcmd(trust_cmd)
    if r.failed:
        api.fail("Could not add CA '%s' to the system's trust DB"
                 % ca_location)
    else:
        api.info("CA '%s' added to system's trust DB" % ca_location)


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
        self.location = None

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
                self.location = ca_dest
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
                          "-subj '%s' -config openssl.cnf"
                          % (hash, subject)))
            utils.runcmd(("openssl x509 -req -in cert.req -CA ca.pem -CAkey "
                          "ca.key -CAcreateserial -extensions v3_req -extfile "
                          "openssl.cnf -out cert.crt -days 1"))

            if key_prv:
                utils.runcmd("chmod 600 cert.key")
                utils.runcmd("cp cert.key %s" % key_prv)
                api.info("Private key stored in '%s' (with 600 perms)."
                         % key_prv)
            if key_pub:
                utils.runcmd("cp cert.crt %s" % key_pub)
                api.info("Public key stored in '%s'." % key_pub)

        return OwnCACert(subject)

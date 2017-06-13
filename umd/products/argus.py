import os.path

from umd import api
from umd import base
from umd.base.configure.ansible import AnsibleConfig
from umd.base.configure.puppet import PuppetConfig
from umd.base.configure.yaim import YaimConfig
from umd import config
from umd import system
from umd import utils


class ArgusDeploy(base.Deploy):
    def pre_config(self):
        # extra vars
        extra_vars = [
            "pap_host: %s" % system.fqdn,
            "pap_port: 8150",
            "pap_host_dn: %s" % config.CFG["cert"].subject,
            "pap_admin_dn: %s" % config.CFG["cert"].subject,
            "pap_port_shutdown: 8151",
            "pap_host_cert: /etc/grid-security/hostcert.pem",
            "pap_host_key: /etc/grid-security/hostkey.pem",
            "pdp_host: %s" % system.fqdn,
            "pdp_port: 8152",
            "pdp_port_admin: 8153",
            "pdp_host_cert: /etc/grid-security/hostcert.pem",
            "pdp_host_key: /etc/grid-security/hostkey.pem",
            "pepd_host: %s" % system.fqdn,
            "pepd_port: 8154",
            "pepd_port_admin: 8155",
            "pepd_host_cert: /etc/grid-security/hostcert.pem",
            "pepd_host_key: /etc/grid-security/hostkey.pem"]
        self.cfgtool.extra_vars = extra_vars


#class ArgusPuppetDeploy(base.Deploy):
#    def pre_config(self):
#        # NOTE(orviz) Check needed since there are official modules
#        # that does not contain metadata.json file
#        api.info(("Puppet <cernops/puppet-argus> module does not contain a "
#                  "valid metadata.json file. Installing manually.."))
#        mod = self.cfgtool.module_from_repository.pop()
#        dest = "/tmp/master.tar.gz"
#        utils.runcmd("wget %s -O %s" % (mod, dest))
#        utils.runcmd("tar xvfz %s -C %s" % (dest, self.cfgtool.module_path))
#        utils.runcmd("mv %s %s" % (
#            os.path.join(self.cfgtool.module_path, "puppet-argus-master"),
#            os.path.join(self.cfgtool.module_path, "argus")))
#
#
#class EESDeploy(base.Deploy):
#    def pre_validate(self):
#        utils.runcmd("useradd -r ees")
#        utils.runcmd("/etc/init.d/ees start")
#        utils.install("nc")


argus = ArgusDeploy(
    name="argus",
    doc="ARGUS server deployment using Ansible.",
    #metapkg="argus-authz",
    need_cert=True,
    has_infomodel=True,
    cfgtool=AnsibleConfig(
        role="https://github.com/egi-qc/ansible-argus"),)

#argus_puppet = ArgusPuppetDeploy(
#    name="argus-puppet",
#    doc="ARGUS server deployment using Puppet.",
#    metapkg="emi-argus",
#    need_cert=True,
#    has_infomodel=True,
#    cfgtool=PuppetConfig(
#        manifest="argus.pp",
#        module_from_repository=("https://github.com/cernops/puppet-argus/"
#                                "archive/master.tar.gz"),
#        module_from_puppetforge="puppetlabs-stdlib"),
#    qc_specific_id="argus")
#
#argus_puppet_no_metapkg = ArgusPuppetDeploy(
#    name="argus-puppet-no-metapkg",
#    doc="ARGUS server with no metapackage deployment.",
#    metapkg=["argus-pap", "argus-pdp", "argus-pep-server"],
#    need_cert=True,
#    has_infomodel=True,
#    cfgtool=PuppetConfig(
#        manifest="argus.pp",
#        module_from_repository=("https://github.com/cernops/puppet-argus/"
#                                "archive/master.tar.gz"),
#        module_from_puppetforge="puppetlabs-stdlib"),
#    qc_specific_id="argus")
#
#argus_yaim = base.Deploy(
#    name="argus",
#    doc="ARGUS server deployment using YAIM.",
#    metapkg="emi-argus",
#    need_cert=True,
#    has_infomodel=True,
#    cfgtool=YaimConfig(
#        nodetype="ARGUS_server",
#        siteinfo=["site-info-ARGUS_server.def"]),
#    qc_specific_id="argus")
#
#ees = EESDeploy(
#    name="argus-ees",
#    doc="ARGUS EES daemon deployment.",
#    metapkg="ees",
#    qc_specific_id="argus-ees")

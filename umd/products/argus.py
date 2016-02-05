import os.path

from umd import api
from umd import base
from umd.base.configure.puppet import PuppetConfig
from umd.base.configure.yaim import YaimConfig
from umd import utils


class ArgusDeploy(base.Deploy):
    def pre_config(self):
        # NOTE(orviz) Check needed since there are official modules
        # that does not contain metadata.json file
        api.info(("Puppet <cernops/puppet-argus> module does not contain a "
                  "valid metadata.json file. Installing manually.."))
        mod = self.cfgtool.module_from_repository.pop()
        dest = "/tmp/master.tar.gz"
        utils.runcmd("wget %s -O %s" % (mod, dest))
        utils.runcmd("tar xvfz %s -C %s" % (dest, self.cfgtool.module_path))
        utils.runcmd("mv %s %s" % (
            os.path.join(self.cfgtool.module_path, "puppet-argus-master"),
            os.path.join(self.cfgtool.module_path, "argus")))


class EESDeploy(base.Deploy):
    def pre_validate(self):
        utils.runcmd("useradd -r ees")
        utils.runcmd("/etc/init.d/ees start")
        utils.install("nc")


argus = ArgusDeploy(
    name="argus",
    doc="ARGUS server deployment using Puppet.",
    metapkg="emi-argus",
    need_cert=True,
    has_infomodel=True,
    cfgtool=PuppetConfig(
        manifest="argus.pp",
        module_from_repository=("https://github.com/cernops/puppet-argus/"
                                "archive/master.tar.gz"),
        module_from_puppetforge="puppetlabs-stdlib"),
    qc_specific_id="argus")

argus_yaim = base.Deploy(
    name="argus",
    doc="ARGUS server deployment using YAIM.",
    metapkg="emi-argus",
    need_cert=True,
    has_infomodel=True,
    cfgtool=YaimConfig(
        nodetype="ARGUS_server",
        siteinfo=["site-info-ARGUS_server.def"]),
    qc_specific_id="argus")

ees = EESDeploy(
    name="argus-ees",
    doc="ARGUS EES daemon deployment.",
    metapkg="ees",
    qc_specific_id="argus-ees")

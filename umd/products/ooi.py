from umd import base
from umd.base.configure.puppet import PuppetConfig
from umd import config


class OOIDeploy(base.Deploy):
    def pre_config(self):
        os_release = config.CFG["openstack_release"]
        self.cfgtool.extra_vars = "ooi::openstack_version: %s" % os_release


ooi = OOIDeploy(
    name="ooi",
    doc="OCCI OpenStack Interface.",
    cfgtool=PuppetConfig(
        manifest="ooi.pp",
        module=("git://github.com/egi-qc/puppet-ooi.git", "umd"),
    ),
    qc_specific_id="ooi",
)

import os.path

from umd import api
from umd import base
from umd.base.configure.puppet import PuppetConfig
from umd import config
from umd import utils


class OOIDeploy(base.Deploy):
    def pre_config(self):
        os_release = config.CFG["openstack_release"]
        ooi_params = "ooi::openstack_version: %s" % os_release
        ooi_conf = os.path.join(config.CFG["cfgtool"].hiera_data_dir,
                                "ooi.yaml")
        if utils.to_yaml(ooi_conf, ooi_params):
            api.info("OOI hiera parameters set: %s" % ooi_conf)
        # Add it to hiera.yaml
        config.CFG["cfgtool"]._add_hiera_param_file("ooi.yaml")


ooi = OOIDeploy(
    name="ooi",
    doc="OCCI OpenStack Interface.",
    cfgtool=PuppetConfig(
        manifest="ooi.pp",
        module=("git://github.com/egi-qc/puppet-ooi.git", "umd"),
    ),
    # qc_specific_id="ooi",
)

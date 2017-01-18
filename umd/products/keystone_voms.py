import os.path

from umd import api
from umd import base
from umd.base.configure.puppet import PuppetConfig
from umd.common import pki
from umd import config
from umd.products import utils as product_utils
from umd.products import voms
from umd import system
from umd import utils


class KeystoneVOMSDeploy(base.Deploy):
    def pre_config(self):
        os_release = config.CFG["openstack_release"]
        self.cfgtool.module.append((
            "git://github.com/egi-qc/puppet-keystone.git",
            "umd_stable_%s" % os_release))
        keystone_voms_params = [
            "keystone_voms::openstack_version: %s" % os_release,
            "cacert: %s" % config.CFG["ca"].location]
        keystone_voms_conf = os.path.join(config.CFG["cfgtool"].hiera_data_dir,
                                "keystone_voms.yaml")
        if utils.to_yaml(keystone_voms_conf, keystone_voms_params):
            api.info("keystone-voms hiera parameters set: %s" % keystone_voms_conf)
        # Add it to hiera.yaml
        config.CFG["cfgtool"]._add_hiera_param_file("keystone_voms.yaml")
        pki.trust_ca(config.CFG["ca"].location)

    #def pre_validate(self):
    #    # voms packages
    #    voms.client_install()
    #    utils.runcmd("pip install voms-auth-system-openstack")
    #    # fake proxy
    #    product_utils.create_fake_proxy()
    #    # fake voms server - lsc
    #    product_utils.add_fake_lsc()


keystone_voms = KeystoneVOMSDeploy(
    name="keystone-voms",
    doc="Keystone VOMS module.",
    need_cert=True,
    cfgtool=PuppetConfig(
        manifest="keystone_voms.pp",
        hiera_data=["voms.yaml"],
        # NOTE(orviz) either we use a generic 'umd' branch
        # or if it is per OS release, it has to be set in pre_config() above
        module=["lcgdm-voms"],
    ),
    qc_specific_id="keystone-voms",
)

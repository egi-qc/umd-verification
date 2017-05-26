import os.path

from umd import api
from umd import base
from umd.base.configure.puppet import PuppetConfig
from umd.common import pki
from umd import config
from umd import utils
from umd import system
from umd.products import utils as product_utils
from umd.products import voms


class KeystoneVOMSDeploy(base.Deploy):
    def pre_config(self):
        os_release = config.CFG["openstack_release"]
        self.cfgtool.module.append((
            "git://github.com/egi-qc/puppet-keystone.git",
            "umd_stable_%s" % os_release))
        keystone_voms_params = [
            "keystone_voms::openstack_version: %s" % os_release,
            "cacert: %s" % config.CFG["ca"].location
        ]
        keystone_voms_conf = os.path.join(
            config.CFG["cfgtool"].hiera_data_dir,
            "keystone_voms.yaml")
        if utils.to_yaml(keystone_voms_conf, keystone_voms_params):
            api.info(("keystone-voms hiera parameters "
                      "set: %s" % keystone_voms_conf))
        # Add it to hiera.yaml
        config.CFG["cfgtool"]._add_hiera_param_file("keystone_voms.yaml")
        pki.trust_ca(config.CFG["ca"].location)

        # FIXME Create tenant VO:dteam
        if system.distro_version == "ubuntu16":
            utils.runcmd("/etc/init.d/apache2 restart")
        elif system.distro_version == "centos7":
            utils.runcmd("systemctl restart httpd")
        utils.runcmd(("/bin/bash -c 'source /root/.nova/admin-novarc ; "
                      "openstack --os-password $OS_PASSWORD "
                      "--os-username $OS_USERNAME "
                      "--os-project-name $OS_PROJECT_NAME "
                      "--os-auth-url $OS_AUTH_URL "
                      "--os-cacert $OS_CACERT "
                      "project create --enable VO:dteam --or-show'"))

    def pre_validate(self):
        # voms packages
        if system.distro_version == "ubuntu16":
            utils.install(["http://mirrors.kernel.org/ubuntu/pool/universe/v/voms/voms-clients_2.0.12-4build1_amd64.deb",
                           "http://launchpadlibrarian.net/229641205/myproxy_6.1.16-1_amd64.deb"])
        elif system.distro_version == "centos7":
            # FIXME Enable epel to install voms clients (remove this when epel clients in CentOS7)
            api.info("Temporary enable epel-release to install voms clients")
            utils.install("epel-release")
        voms.client_install()
        utils.runcmd("pip install voms-auth-system-openstack")
        # fake proxy
        product_utils.create_fake_proxy()
        # fake voms server - lsc
        product_utils.add_fake_lsc()


keystone_voms = KeystoneVOMSDeploy(
    name="keystone-voms",
    doc="Keystone VOMS module deployment leveraging Devstack.",
    need_cert=True,
    cfgtool=PuppetConfig(
        manifest="keystone_voms.pp",
        hiera_data=["voms.yaml"],
        module=["puppetlabs-inifile",
                "puppetlabs-apache",
                "lcgdm-voms"],
    ),
    qc_specific_id="keystone-voms",
)

keystone_voms_full = KeystoneVOMSDeploy(
    name="keystone-voms-full",
    doc="Keystone service & Keystone VOMS module deployment.",
    need_cert=True,
    cfgtool=PuppetConfig(
        manifest="keystone_voms_full.pp",
        hiera_data=["voms.yaml"],
        # NOTE(orviz) either we use a generic 'umd' branch
        # or if it is per OS release, it has to be set in pre_config() above
        #module=[("git://github.com/egi-qc/puppet-keystone.git", "umd_stable_mitaka"), "lcgdm-voms"],
        module=["puppetlabs-inifile", "lcgdm-voms"],
    ),
    qc_specific_id="keystone-voms",
)

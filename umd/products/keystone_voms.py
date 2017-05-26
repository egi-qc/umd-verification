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

        # Apache2
        if system.distro_version == "ubuntu16":
            utils.runcmd(("sed -e '/ServerName*/c\ServerName %s' "
                          "/etc/apache2/apache2.conf") % system.fqdn)
            utils.runcmd("/etc/init.d/apache2 restart")
        elif system.distro_version == "centos7":
            utils.runcmd(("sed -e '/ServerName*/c\ServerName %s' "
                          "/etc/httpd/conf/httpd.conf") % system.fqdn)
            utils.runcmd("systemctl restart httpd")

        # mysql - set current hostname
        utils.runcmd("mysql -e 'UPDATE keystone.endpoint SET url=\"https://%s:5000/v2.0\" WHERE url like \"%%5000%%v2.0%%\";'" % system.fqdn) 
        utils.runcmd("mysql -e 'UPDATE keystone.endpoint SET url=\"https://%s:35357/v2.0\" WHERE url like \"%%35357%%v2.0%%\";'" % system.fqdn) 

        # FIXME Create tenant VO:dteam
        utils.runcmd(("/bin/bash -c 'source /root/.nova/admin-novarc ; "
                      "openstack --os-password $OS_PASSWORD "
                      "--os-username $OS_USERNAME "
                      "--os-project-name $OS_PROJECT_NAME "
                      "--os-auth-url $OS_AUTH_URL "
                      "--os-cacert $OS_CACERT "
                      "project create --enable VO:dteam --or-show'"))

    def pre_validate(self):
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

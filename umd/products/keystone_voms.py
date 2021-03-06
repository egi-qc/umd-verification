# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

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
        utils.runcmd(("mysql -e 'UPDATE keystone.endpoint SET "
                      "url=\"https://%s:5000/v2.0\" WHERE url "
                      "like \"%%5000%%\";'" % system.fqdn))
        utils.runcmd(("mysql -e 'UPDATE keystone.endpoint SET "
                      "url=\"https://%s:35357/v2.0\" WHERE url "
                      "like \"%%35357%%\";'" % system.fqdn))

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
        config.CFG["x509_user_proxy"] = product_utils.create_fake_proxy()
        # fake voms server - lsc
        product_utils.add_fake_lsc()

        # If Ubuntu, token must be retrieved using curl calls
        if system.distro_version == "ubuntu16":
            config.CFG["qc_specific_id"] = "keystone-voms-ubuntu"


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
        # module=[("git://github.com/egi-qc/puppet-keystone.git",
        # "umd_stable_mitaka"), "lcgdm-voms"],
        module=["puppetlabs-inifile", "lcgdm-voms"],
    ),
    qc_specific_id="keystone-voms",
)

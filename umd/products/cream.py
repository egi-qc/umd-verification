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

from umd import base
from umd.base.configure.puppet import PuppetConfig
from umd import config
from umd.products import utils as product_utils
from umd.products import voms
from umd import utils


class CreamCEDeploy(base.Deploy):
    def pre_validate(self):
        voms.client_install()
        utils.install("glite-ce-cream-cli")
        if not config.CFG.get("x509_user_proxy", None):
            # fake proxy
            config.CFG["x509_user_proxy"] = product_utils.create_fake_proxy()
            # fake voms server - lsc
            product_utils.add_fake_lsc()


cream = CreamCEDeploy(
    name="cream",
    need_cert=True,
    has_infomodel=True,
    cfgtool=PuppetConfig(
        manifest="cream.pp",
        hiera_data="cream.yaml",
        module=["git://github.com/egi-qc/puppet-slurm.git",
                # "infnpd-creamce",
                "git://github.com/egi-qc/puppet-creamce.git",
                "puppetlabs-firewall"]),
    qc_specific_id="cream")

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
from umd.products import utils as product_utils
from umd.products import voms
from umd import utils


class GridFTPDeploy(base.Deploy):
    def pre_validate(self):
        # voms packages
        utils.install("globus-gass-copy-progs")
        voms.client_install()
        # fake proxy
        product_utils.create_fake_proxy()
        # fake voms server - lsc
        product_utils.add_fake_lsc()


gridftp = GridFTPDeploy(
    name="gridftp",
    doc="Globus GridFTP server deployment using Puppet.",
    need_cert=True,
    cfgtool=PuppetConfig(
        manifest="gridftp.pp",
        hiera_data="gridftp.yaml",
        module=("git://github.com/cern-it-sdc-id/puppet-gridftp", "master"),
    ),
    qc_specific_id="gridftp")

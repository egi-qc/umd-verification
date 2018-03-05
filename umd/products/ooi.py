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

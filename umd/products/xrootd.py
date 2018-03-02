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
from umd import utils


class XRootdDeploy(base.Deploy):
    def pre_validate(self):
        utils.install("xrootd-client")


xrootd = XRootdDeploy(
    name="xrootd",
    doc="xrootd deployment using Puppet.",
    cfgtool=PuppetConfig(
        manifest="xrootd.pp",
        hiera_data=["xrootd.yaml"],
        module=[
            ("git://github.com/egi-qc/puppet-xrootd.git", "umd"),
            "puppet-fetchcrl"]),
    qc_specific_id="xrootd",
)

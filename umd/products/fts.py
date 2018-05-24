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

class FTSDeploy(base.Deploy):
    def pre_config(self):
        # extra vars
        extra_vars = [
            # CA repo configured by external fetchcrl module
            "igtf_repo: false"]
        self.cfgtool.extra_vars = extra_vars

fts = FTSDeploy(
    name="fts",
    doc="File Transfer Service (FTS) deployment.",
    need_cert=True,
    cfgtool=PuppetConfig(
        manifest="fts.pp",
        hiera_data=["fts.yaml", "fetchcrl.yaml"],
        module=[
            ("git://github.com/egi-qc/puppet-fts.git", "umd"),
            ("git://github.com/voxpupuli/puppet-fetchcrl.git", "master"),
            "puppetlabs-firewall",
            "puppetlabs-stdlib",
            "cprice404-inifile",
            "domcleal-augeasproviders",
            "erwbgy-limits"]),
)

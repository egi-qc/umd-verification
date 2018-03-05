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
from umd import system
from umd import utils


class DPMDeploy(base.Deploy):
    def pre_config(self):
        # extra vars
        if system.distro_version == "redhat6":
            extra_vars = ["voms_clientpkgs: voms-clients"]
            self.cfgtool.extra_vars = extra_vars
        # /etc/lcgdm-mapfile content
        dteam_dn = ("/DC=org/DC=terena/DC=tcs/C=ES/O=Consejo Superior de "
                    "Investigaciones Cientificas/CN=PABLO ORVIZ FERNANDEZ "
                    "594361@csic.es")
        utils.write_to_file("/etc/lcgdm-mapfile",
                            dteam_dn,
                            mode='w')


dpm = DPMDeploy(
    name="dpm",
    doc="DPM deployment using Puppet.",
    need_cert=True,
    cfgtool=PuppetConfig(
        manifest="dpm.pp",
        module=[
            "puppetlabs-stdlib",
            "git://github.com/egi-qc/puppet-dpm.git",
            # "git://github.com/cern-it-sdc-id/puppet-dpm",
        ]),
)

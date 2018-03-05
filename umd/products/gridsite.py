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
from umd.base.configure.script import ScriptConfig
from umd import system
from umd import utils


class GridSiteDeploy(base.Deploy):
    def pre_config(self):
        utils.install(["ca-policy-egi-core", "httpd", "mod_ssl"])
        if system.distro_version == "redhat6":
            self.cfgtool.script = "./bin/gridsite/configure_sl6.sh"


gridsite = GridSiteDeploy(
    name="gridsite",
    doc="Gridsite installation",
    metapkg=[
        "gridsite",
        # "gridsite-clients",
        # "gridsite-devel",
        # "gridsite-doc",
        "gridsite-service-clients",
        "gridsite-commands",
        # "gridsite1.7-compat",
    ],
    need_cert=True,
    cfgtool=ScriptConfig("./bin/gridsite/configure.sh"),
    qc_specific_id="gridsite")

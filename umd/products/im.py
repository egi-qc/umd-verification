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
from umd.base.configure.ansible import AnsibleConfig
from umd import utils


class IMDeploy(base.Deploy):
    def pre_config(self):
        # extra vars
        extra_vars = ["im_version: distribution"]
        self.cfgtool.extra_vars = extra_vars

    def pre_validate(self):
        utils.runcmd("pip install IM-client")


im = IMDeploy(
    name="im",
    doc="Infrastructure Manager deployment using Ansible.",
    cfgtool=AnsibleConfig(
        role="https://github.com/egi-qc/ansible-role-im",
        checkout="umd"),
    qc_specific_id="im")

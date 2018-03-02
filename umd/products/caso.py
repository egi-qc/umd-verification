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


class CasoDeploy(base.Deploy):
    def pre_config(self):
        ip = utils.runcmd("hostname -I | cut -d' ' -f1")
        # extra vars
        extra_vars = [
            "site_name: UMD",
            "projects: demo",
            "extractor: nova",
            "auth_type: password",
            "auth_url: http://%s/identity" % ip,
            "username: admin",
            "user_domain_name: default",
            "password: secret",
            "output_path: /var/spool/apel/outgoing/openstack",
            "vos: { \"demo\": [\"demo\"]}"]
        self.cfgtool.extra_vars = extra_vars


caso = CasoDeploy(
    name="caso",
    doc="Accounting parser for OpenStack (caso) deployment using Ansible.",
    cfgtool=AnsibleConfig(
        role="https://github.com/egi-qc/ansible-caso"),
    qc_specific_id="caso")

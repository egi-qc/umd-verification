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
from umd import config


class ArcCEAnsibleDeploy(base.Deploy):
    def pre_config(self):
        # extra vars
        extra_vars = [
            "arc_x509_user_key: %s" % config.CFG["cert"].key_path,
            "arc_x509_user_cert: %s" % config.CFG["cert"].cert_path]
        self.cfgtool.extra_vars = extra_vars

arc_ce = ArcCEAnsibleDeploy(
    name="arc-ce",
    doc="ARC computing element server deployment.",
    need_cert=True,
    has_infomodel=True,
    cfgtool=AnsibleConfig(
        role="https://github.com/egi-qc/ansible-arc"),)

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
from umd.base.configure.puppet import PuppetConfig


clients_solo = base.Deploy(
    name="clients-solo",
    doc="Grid client tools (only installation).",
    cfgtool=AnsibleConfig(
        role="https://github.com/egi-qc/ansible-grid-clients"),)

clients_solo_puppet = base.Deploy(
    name="clients-solo-puppet",
    doc="Grid client tools (only installation).",
    cfgtool=PuppetConfig(
        manifest="clients_solo.pp")
)

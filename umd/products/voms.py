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

from umd import utils


def client_install():
    utils.install([
        "voms-clients",
        "myproxy"
    ])

# voms_server = base.Deploy(
#     name="voms-mysql",
#     doc="MySQL VOMS server deployment.",
#     metapkg="emi-voms-mysql",
#     need_cert=True,
#     has_infomodel=True)

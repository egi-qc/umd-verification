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
from umd import system


class ArgusDeploy(base.Deploy):
    def pre_config(self):
        # extra vars
        extra_vars = [
            "pap_host: %s" % system.fqdn,
            "pap_port: 8150",
            "pap_host_dn: %s" % config.CFG["cert"].subject,
            "pap_admin_dn: %s" % config.CFG["cert"].subject,
            "pap_port_shutdown: 8151",
            "pap_host_cert: /etc/grid-security/hostcert.pem",
            "pap_host_key: /etc/grid-security/hostkey.pem",
            "pdp_host: %s" % system.fqdn,
            "pdp_port: 8152",
            "pdp_port_admin: 8153",
            "pdp_host_cert: /etc/grid-security/hostcert.pem",
            "pdp_host_key: /etc/grid-security/hostkey.pem",
            "pepd_host: %s" % system.fqdn,
            "pepd_port: 8154",
            "pepd_port_admin: 8155",
            "pepd_host_cert: /etc/grid-security/hostcert.pem",
            "pepd_host_key: /etc/grid-security/hostkey.pem"]
        self.cfgtool.extra_vars = extra_vars

argus = ArgusDeploy(
    name="argus",
    doc="ARGUS server deployment using Ansible.",
    need_cert=True,
    has_infomodel=True,
    cfgtool=AnsibleConfig(
        role="https://github.com/egi-qc/ansible-argus"),)

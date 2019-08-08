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


class CloudInfoProviderDeploy(base.Deploy):
    def pre_config(self):
        # extra vars
        extra_vars = [
            "cloud_info_provider_os_release: %s "
            % config.CFG["openstack_release"],
            "cloud_info_provider_middleware: openstack ",
            "cloud_info_provider_conf_dir: /etc/cloud-info-provider ",
            "cloud_info_provider_bdii_dir: /var/lib/bdii/gip/provider"]
        self.cfgtool.extra_vars = extra_vars


cloud_info_provider = CloudInfoProviderDeploy(
    name="cloud-info-provider",
    doc="cloud-info-provider deployment using Ansible.",
    # NOTE(orviz) glue-validator is not yet available in CMD
    # The check is done in QC_FUNC_1
    # has_infomodel=True,
    cfgtool=AnsibleConfig(
        role="https://github.com/egi-qc/ansible-role-cloud-info-provider",
        checkout="umd",
        tags=["untagged", "cmd"]),
    qc_specific_id="cloud-info-provider")

from umd import base
from umd.base.configure.ansible import AnsibleConfig
from umd import config
from umd import system


class CloudInfoProviderDeploy(base.Deploy):
    def pre_config(self):
        # extra vars
        extra_vars = ("distribution=cmd "
                      "verification_repofile=%s "
                      "cloud_info_provider_os_release=%s"
                      "cloud_info_provider_middleware=openstack"
                      "cloud_info_provider_conf_dir=/etc/cloud-info-provider "
                      % (config.CFG["repository_file"],
                         config.CFG["openstack_release"]))
        self.cfgtool.extra_vars = extra_vars


cloud_info_provider = CloudInfoProviderDeploy(
    name="cloud-info-provider",
    doc="cloud-info-provider deployment using Ansible.",
    has_infomodel=True,
    cfgtool=AnsibleConfig(
        role = "https://github.com/egi-qc/ansible-role-cloud-info-provider",
        checkout = "umd",
        tags = "untagged"))

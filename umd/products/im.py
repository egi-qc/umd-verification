from umd import base
from umd.base.configure.ansible import AnsibleConfig


class IMDeploy(base.Deploy):
    def pre_config(self):
        # extra vars
        extra_vars = ["im_version: distribution"]
        self.cfgtool.extra_vars = extra_vars

im = IMDeploy(
    name="im",
    doc="Infrastructure Manager deployment using Ansible.",
    cfgtool=AnsibleConfig(
        role="https://github.com/egi-qc/ansible-role-im",
        checkout="umd"),)

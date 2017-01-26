from umd import base
from umd.base.configure.ansible import AnsibleConfig
from umd import utils


myproxy = base.Deploy(
    name="myproxy",
    doc="MyProxy server deployment using Ansible.",
    need_cert=True,
    has_infomodel=True,
    cfgtool=AnsibleConfig(
        role="https://github.com/egi-qc/ansible-myproxy"),)

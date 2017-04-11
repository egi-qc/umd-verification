from umd import base
from umd.base.configure.ansible import AnsibleConfig


caso = base.Deploy(
    name="caso",
    doc="Accounting parser for OpenStack (caso) deployment using Ansible.",
    cfgtool=AnsibleConfig(
        role="https://github.com/egi-qc/ansible-caso"),)

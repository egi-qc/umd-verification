import os.path

from umd import api
from umd import base
from umd.base.configure.ansible import AnsibleConfig
from umd import config
from umd import system
from umd import utils


ui = base.Deploy(
    name="user-interface",
    doc="User interface deployment using Ansible.",
    cfgtool=AnsibleConfig(
        role="https://github.com/egi-qc/ansible-ui"),)

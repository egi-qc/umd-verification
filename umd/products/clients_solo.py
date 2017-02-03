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

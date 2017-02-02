from umd import base
from umd.base.configure.puppet import PuppetConfig


clients_solo = base.Deploy(
    name="clients-solo",
    doc="Grid client tools (only installation).",
    cfgtool=PuppetConfig(
        manifest="clients_solo.pp")
)

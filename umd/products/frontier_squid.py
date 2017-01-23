from umd import base
from umd.base.configure.puppet import PuppetConfig


frontier_squid = base.Deploy(
    name="frontier-squid",
    doc="Frontier Squid cache server deployment.",
    need_cert=True,
    cfgtool=PuppetConfig(
        manifest="frontier_squid.pp",
        module="desalvo-frontier",
    ),
    qc_specific_id="frontier-squid",
)

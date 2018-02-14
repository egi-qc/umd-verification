from umd import base
from umd.base.configure.puppet import PuppetConfig

dpm = base.Deploy(
    name="dpm",
    doc="DPM deployment using Puppet.",
    need_cert=True,
    cfgtool=PuppetConfig(
        manifest="dpm.pp",
        module=[
            "puppetlabs-stdlib",
            "git://github.com/egi-qc/puppet-dpm.git",
            ]),
)

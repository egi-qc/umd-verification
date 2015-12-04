from umd import base
from umd.base.configure.puppet import PuppetConfig

dpm_1_8_10 = base.Deploy(
    name="dpm-1_8_10",
    doc="DPM deployment with Puppet.",
    metapkg=["emi-dpm_mysql", "emi-dpm_disk"],
    has_infomodel=True,
    need_cert=True,
    cfgtool=PuppetConfig(
        manifest="dpm.pp",
        module_from_puppetforge=[
            "lcgdm-dmlite --version 0.3.10",
            "puppetlabs-firewall",
            "lcgdm-lcgdm --version 0.2.10",
            "lcgdm-gridftp --version 0.1.2",
            "lcgdm-xrootd --version 0.1.2",
            "lcgdm-voms --version 0.2.0",
            "puppetlabs-mysql",
            "saz-memcached",
            "CERNOps-bdii",
            "CERNOps-fetchcrl",
            "erwbgy-limits "]),
    qc_specific_id="dpm"
)

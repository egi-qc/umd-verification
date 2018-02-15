from umd import base
from umd.base.configure.puppet import PuppetConfig


xrootd = base.Deploy(
    name="xrootd",
    doc="xrootd deployment using Puppet.",
    cfgtool=PuppetConfig(
        manifest="xrootd.pp",
        hiera_data=["xrootd.yaml"],
        module=[
            ("git://github.com/egi-qc/puppet-xrootd.git", "umd"),
            "puppet-fetchcrl"]),
    qc_specific_id="xrootd",
)

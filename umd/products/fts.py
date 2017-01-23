from umd import base
from umd.base.configure.puppet import PuppetConfig


fts = base.Deploy(
    name="fts",
    doc="File Transfer Service (FTS) deployment.",
    need_cert=True,
    cfgtool=PuppetConfig(
        manifest="fts.pp",
        hiera_data=["fts.yaml", "fetchcrl.yaml"],
        module=[
            ("git://github.com/egi-qc/puppet-fts.git", "umd"),
            ("git://github.com/voxpupuli/puppet-fetchcrl.git", "master"),
            "puppetlabs-firewall",
            "puppetlabs-stdlib",
            "cprice404-inifile",
            "domcleal-augeasproviders",
            "erwbgy-limits"]),
)

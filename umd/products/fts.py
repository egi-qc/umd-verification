from umd import base
from umd.base.configure.puppet import PuppetConfig
from umd import system


class FTSDeploy(base.Deploy):
    def pre_config(self):
        if system.distro_version == "redhat6":
            _schema = "/usr/share/fts-mysql/mysql-schema.sql"
            self.cfgtool.extra_vars = "fts_schema: %s" % _schema


fts = FTSDeploy(
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

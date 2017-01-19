from umd import base
from umd.base.configure.puppet import PuppetConfig
from umd import config
from umd import system
from umd import utils


class FTSDeploy(base.Deploy):
    def post_config(self):
        hiera_config = utils.load_from_hiera(
            config.CFG["cfgtool"].hiera_data)
        db_name = hiera_config["fts3_db_name"]
        db_user = hiera_config["fts3_db_username"]
        db_pass = hiera_config["fts3_db_password"]

        # mysql
        if system.distro_version == "centos7":
            pkg_server = "mariadb-server"
            cmd_start = "systemctl start mariadb"
        elif system.distro_version == "ubuntu14":
            pkg_server = "mysql-server"
            cmd_start = "service mysql start"
        utils.install(pkg_server)
        utils.runcmd(cmd_start, stop_on_error=False)
        utils.runcmd("mysql -e \"drop database IF EXISTS ftsdb\"")
        utils.runcmd("mysql -e \"create database %s\"" % db_name)
        utils.runcmd("mysql ftsdb < /usr/share/fts-mysql/mysql-schema.sql")
        utils.runcmd(("mysql -e \"GRANT ALL ON %s.* TO %s@'localhost' "
                      "IDENTIFIED BY '%s';\""
                     % (db_name, db_user, db_pass)))
        utils.runcmd("mysql -e \"FLUSH PRIVILEGES;\"")

        # httpd
        utils.install("mod_ssl")


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

from umd import base
from umd.base.configure.puppet import PuppetConfig
from umd import utils


class FTSDeploy(base.Deploy):
    def pre_config(self):
        db_name = utils.runcmd(("hiera -c /etc/puppet/hiera.yaml "
                                "fts3_db_name"))
        db_user = utils.runcmd(("hiera -c /etc/puppet/hiera.yaml "
                                "fts3_db_username"))
        db_pass = utils.runcmd(("hiera -c /etc/puppet/hiera.yaml "
                                "fts3_db_password"))

        # mysql
        utils.install("mysql-server")
        utils.runcmd("service mysqld start")
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
    metapkg=["fts-server",
             "fts-client",
             "fts-rest",
             "fts-monitoring",
             "fts-mysql",
             "fts-server-selinux"],
    need_cert=True,
    cfgtool=PuppetConfig(
        manifest="fts.pp",
        hiera_data="fts.yaml",
        module_from_puppetforge=["CERNOps-fts",
                                 "CERNOps-fetchcrl",
                                 "puppetlabs-firewall",
                                 "puppetlabs-stdlib",
                                 "cprice404-inifile",
                                 "domcleal-augeasproviders",
                                 "erwbgy-limits"]))

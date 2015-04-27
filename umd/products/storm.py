from fabric.api import local
from fabric.api import puts
from fabric.colors import green

from umd.base import Deploy


class StormSL5Deploy(Deploy):
    """Single-node Storm deployment."""
    def pre_install(self):
        puts(green("PRE-install actions."))

        local("/usr/sbin/adduser -M storm")

        puts(green("users storm and gridhttps added"))
        puts(green("END of PRE-install actions."))

    def pre_config(self):
        puts(green("PRE-config actions."))

        self.pkgtool.install(pkgs=["ntp", "ca-policy-egi-core"])
        puts(green("<ntp, ca-policy-egi-core> installed."))

        local("mount -o remount,acl,user_xattr /")
        puts(green("Enabled ACLs and Extended Attribute Support in /"))

        puts(green("END of PRE-config actions."))

    def pre_validate(self):
        puts(green("PRE-validate actions."))

        pkgs = ["storm-srm-client", "uberftp", "curl",
                "myproxy", "voms-clients", "lcg-util"]
        self.pkgtool.install(pkgs=pkgs)
        puts(green("<%s> installed." % ", ".join(pkgs)))

        puts(green("END of PRE-validate actions."))


sl5 = StormSL5Deploy(
    name="storm-sl5",
    need_cert=True,
    metapkg=["emi-storm-backend-mp", "emi-storm-frontend-mp",
             "emi-storm-globus-gridftp-mp", "emi-storm-gridhttps-mp"],
    nodetype=["se_storm_backend", "se_storm_frontend", "se_storm_gridftp",
              "se_storm_gridhttps"],
    siteinfo=["site-info-storm.def"],
    qc_specific_id="storm")

import pwd

from umd.api import info
from umd.api import install
from umd.api import runcmd
from umd.base import Deploy


class StormDeploy(Deploy):
    """Single-node Storm deployment."""

    pre_validate_pkgs = ["storm-srm-client", "uberftp", "curl", "myproxy",
                         "voms-clients", "lcg-util"]

    def __init__(self, os="sl5"):
        name = "-".join(["storm", os])
        metapkg = ["emi-storm-backend-mp", "emi-storm-frontend-mp",
                   "emi-storm-globus-gridftp-mp"]
        nodetype = ["se_storm_backend", "se_storm_frontend",
                    "se_storm_gridftp"]
        if os == "sl5":
            metapkg.append("emi-storm-gridhttps-mp")
            nodetype.append("se_storm_gridhttps")
            self.pre_validate_pkgs.append("python26-requests")
        elif os == "sl6":
            metapkg.append("storm-webdav")
            nodetype.append("se_storm_webdav")
        super(StormDeploy, self).__init__(name=name, need_cert="True",
                                          metapkg=metapkg, nodetype=nodetype,
                                          siteinfo=["site-info-storm.def"],
                                          qc_specific_id="storm")

    def pre_install(self):
        info("PRE-install actions.")

        try:
            pwd.getpwnam("storm")
        except KeyError:
            runcmd("/usr/sbin/adduser -M storm")

        info("users storm and gridhttps added")
        info("END of PRE-install actions.")

    def pre_config(self):
        info("PRE-config actions.")

        install(pkgs=["ntp"])
        info("<ntp> installed.")

        runcmd("mount -o remount,acl,user_xattr /")
        info("Enabled ACLs and Extended Attribute Support in /")

        info("END of PRE-config actions.")

    def pre_validate(self):
        info("PRE-validate actions.")

        install(pkgs=self.pre_validate_pkgs)
        info("<%s> installed." % ", ".join(self.pre_validate_pkgs))

        info("END of PRE-validate actions.")


sl5 = StormDeploy("sl5")
sl6 = StormDeploy("sl6")

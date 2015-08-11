import pwd

from umd import api
from umd import base
from umd.base.configure.yaim import YaimConfig
from umd import utils


class StormDeploy(base.Deploy):
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
        super(StormDeploy, self).__init__(
            name=name,
            need_cert=True,
            has_infomodel=True,
            metapkg=metapkg,
            cfgtool=YaimConfig(
                nodetype=nodetype,
                siteinfo=["site-info-storm.def"]),
            qc_specific_id="storm")

    def pre_install(self):
        api.info("PRE-install actions.")

        try:
            pwd.getpwnam("storm")
        except KeyError:
            utils.runcmd("/usr/sbin/adduser -M storm")

        api.info("users storm and gridhttps added")
        api.info("END of PRE-install actions.")

    def pre_config(self):
        api.info("PRE-config actions.")

        utils.install("ntp")
        api.info("<ntp> installed.")

        utils.runcmd("mount -o remount,acl,user_xattr /")
        api.info("Enabled ACLs and Extended Attribute Support in /")

        api.info("END of PRE-config actions.")

    def pre_validate(self):
        api.info("PRE-validate actions.")

        utils.install(self.pre_validate_pkgs)
        api.info("<%s> installed." % ", ".join(self.pre_validate_pkgs))

        api.info("END of PRE-validate actions.")


sl5 = StormDeploy("sl5")
sl6 = StormDeploy("sl6")

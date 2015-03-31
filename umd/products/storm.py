from fabric.colors import green
from fabric.colors import yellow
from umd.base import Deploy


class StormSL5Deploy(Deploy):
    """Single-node Storm deployment."""
    def pre_config(self):
        print(yellow("PRE-config actions."))

        self.pkgtool.install(pkgs="ntp")

        print(green("<ntp> package installed."))
        print(yellow("END of PRE-config actions."))


sl5 = StormSL5Deploy(
    name="storm-sl5",
    metapkg=("emi-storm-backend-mp emi-storm-frontend-mp "
             "emi-storm-globus-gridftp-mp emi-storm-gridhttps-mp"),
    nodetype=("se_storm_backend se_storm_frontend se_storm_gridftp "
              "se_storm_gridhttps"),
    siteinfo = ["site-info-storm.def"],
    need_cert=True)

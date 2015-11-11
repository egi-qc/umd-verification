from umd import api
from umd import base
from umd.base.configure.puppet import PuppetConfig
from umd import system
from umd import utils


class ArcCEDeploy(base.Deploy):
    def pre_install(self):
        if system.distro_version == "redhat6":
            api.info(("Installing hwloc version 1.5-1 required by "
                      "emi-torque-client"))
            utils.runcmd(("wget http://ftp.pbone.net/mirror/"
                          "ftp.scientificlinux.org/linux/scientific/6.4/"
                          "x86_64/os/Packages/hwloc-1.5-1.el6.x86_64.rpm"
                          "-O /tmp/hwloc-1.5-1.el6.x86_64.rpm"))
            r = utils.install("/tmp/hwloc-1.5-1.el6.x86_64.rpm",
                              log_to_file="pre_install")
            if r.failed:
                # FIXME(orviz) stop_on_error=True here??
                api.fail("Could not install hwloc version 1.5-1")


arc_ce = ArcCEDeploy(
    name="arc-ce",
    doc="ARC computing element server deployment.",
    metapkg=["nordugrid-arc-compute-element",
             "emi-torque-server"],
    need_cert=True,
    has_infomodel=True,
    cfgtool=PuppetConfig(
        manifest="arc.pp",
        hiera_data=["arc.yaml",
                    "bdii.yaml"],
        module_from_repository=("https://github.com/HEP-Puppet/arc_ce/archive/"
                                "master.tar.gz"),
        module_from_puppetforge=["puppetlabs-firewall",
                                 "puppetlabs-stdlib",
                                 "puppetlabs-concat",
                                 "CERNOps-fetchcrl"]),
)

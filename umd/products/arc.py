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

    def pre_validate(self):
        # Change 'pbs' to 'pbs_server' in /etc/services
        utils.runcmd(("sed -e 's/^pbs .*\/tcp/pbs_server 15001\/tcp/g' "
                      "/etc/services"))
        utils.runcmd(("sed -e 's/^pbs .*\/udp/pbs_server 15001\/udp/g' "
                      "/etc/services"))

        # Set FQDN in /etc/torque/server_name
        fqdn = utils.runcmd("hostname -f")
        utils.runcmd("echo %s > /etc/torque/server_name" % fqdn)

        # Set nodes file
        utils.runcmd("echo \"%s np=1\" > /var/lib/torque/server_priv/nodes"
                     % fqdn)

        # Start services
        utils.runcmd("/etc/init.d/trqauthd restart")
        utils.runcmd("/etc/init.d/pbs_server restart")
        utils.runcmd("create-munge-key -f")
        utils.runcmd("/etc/init.d/munge restart")

        # Torque configuration
        utils.runcmd("qmgr -c \"set server acl_hosts = %s\"" % fqdn)
        utils.runcmd("qmgr -c \"set server scheduling=true\"")
        utils.runcmd("qmgr -c \"create queue batch queue_type=execution\"")
        utils.runcmd("qmgr -c \"set queue batch started=true\"")
        utils.runcmd("qmgr -c \"set queue batch enabled=true\"")
        utils.runcmd("qmgr -c \"set queue batch resources_default.nodes=1\"")
        utils.runcmd(("qmgr -c \"set queue batch resources_default.walltime="
                      "3600\""))
        utils.runcmd("qmgr -c \"set server default_queue=batch\"")


arc_ce = ArcCEDeploy(
    name="arc-ce",
    doc="ARC computing element server deployment.",
    metapkg=["nordugrid-arc-compute-element",
             "emi-torque-server"],
    need_cert=True,
    has_infomodel=True,
    info_port="2135",
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

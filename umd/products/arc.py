from umd import api
from umd import base
from umd.base.configure.puppet import PuppetConfig
from umd import system
from umd import utils

grid_mapfile = """
"/dteam/Role=pilot/Capability=NULL" umd
"/dteam/Role=pilot" umd
"/dteam/Role=NULL/Capability=NULL" umd
"/dteam" umd
"/dteam/*/Role=NULL/Capability=NULL" umd
"/dteam/*" umd
"/ops/Role=lcgadmin/Capability=NULL" umd
"/ops/Role=lcgadmin" umd
"/ops/Role=pilot/Capability=NULL" umd
"/ops/Role=pilot" umd
"/ops/Role=NULL/Capability=NULL" umd
"/ops" umd
"/ops/*/Role=NULL/Capability=NULL" umd
"/ops/*" umd
"/ops.vo.ibergrid.eu/Spain/Role=NULL/Capability=NULL" umd
"/ops.vo.ibergrid.eu/Spain" umd
"/ops.vo.ibergrid.eu/Portugal/Role=NULL/Capability=NULL" umd
"/ops.vo.ibergrid.eu/Portugal" umd
"/ops.vo.ibergrid.eu/Role=SW-Admin/Capability=NULL" umd
"/ops.vo.ibergrid.eu/Role=SW-Admin" umd
"/ops.vo.ibergrid.eu/Role=Production/Capability=NULL" umd
"/ops.vo.ibergrid.eu/Role=Production" umd
"/ops.vo.ibergrid.eu/Role=NULL/Capability=NULL" umd
"/ops.vo.ibergrid.eu" umd
"/ops.vo.ibergrid.eu/*/Role=NULL/Capability=NULL" umd
"/ops.vo.ibergrid.eu/*" umd
"""


class ArcCEDeploy(base.Deploy):
    def _set_control_access(self, sessiondir, scratchdir):
        utils.runcmd("useradd -m umd")

        # Generate grid-mapfile - FIXME(orviz) do it with `nordugridmap`
        with open("/etc/grid-security/grid-mapfile", 'w') as f:
            f.write(grid_mapfile)
            f.flush()

        # session & scratch dir
        utils.runcmd("chown root:umd %s" % sessiondir)
        utils.runcmd("mkdir %s" % scratchdir)
        utils.runcmd("chmod 777 %s" % scratchdir)

    def _set_arc_conf(self, scratchdir):
        arc_conf = "/etc/arc.conf"
        # arex_mount_point (set, commented)
        utils.runcmd("sed -i '/arex_mount_point/s/#//g' %s" % arc_conf)
        # scratchdir (set)
        utils.runcmd("sed -i '/^sessiondir=.*/a scratchdir=\"%s\"' %s"
                     % (scratchdir, arc_conf))
        # defaultmemory
        utils.runcmd(("sed -i 's/^defaultmemory=.*/defaultmemory=\"512\"/g' %s"
                      % arc_conf))
        # authplugin (commented)
        utils.runcmd("sed -i 's/\(^.*#authplugin.*$\)/#\1/' %s" % arc_conf)
        utils.runcmd("/etc/init.d/a-rex restart")

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

    def _set_pbs(self):
        fqdn = utils.runcmd("hostname -f")

        # Change 'pbs' to 'pbs_server' in /etc/services
        utils.runcmd(("sed -i 's/^pbs .*\/tcp/pbs_server 15001\/tcp/g' "
                      "/etc/services"))
        utils.runcmd(("sed -i 's/^pbs .*\/udp/pbs_server 15001\/udp/g' "
                      "/etc/services"))

        # Set pbs and maui parameters
        utils.runcmd("echo %s > /etc/torque/server_name" % fqdn)
        utils.runcmd("echo \"%s np=1\" > /var/lib/torque/server_priv/nodes"
                     % fqdn)
        utils.runcmd("sed -i 's/localhost/%s/g' /var/spool/maui/maui.cfg"
                     % fqdn)
        utils.runcmd(("echo \"\$pbsserver %s\" > "
                      "/var/lib/torque/mom_priv/config" % fqdn))

        # Start services - server
        utils.runcmd("/etc/init.d/trqauthd restart")
        utils.runcmd("/etc/init.d/pbs_server stop")
        utils.runcmd("/etc/init.d/pbs_server start")
        utils.runcmd("create-munge-key -f")
        utils.runcmd("/etc/init.d/munge restart")
        utils.runcmd("/etc/init.d/maui stop ; /etc/init.d/maui start")
        utils.runcmd("/etc/init.d/pbs_mom stop ; /etc/init.d/pbs_mom start")

        # Torque configuration
        utils.runcmd("qmgr -c \"set server acl_hosts = %s\"" % fqdn)
        utils.runcmd("qmgr -c \"set server scheduling=true\"")
        utils.runcmd("qmgr -c \"create queue batch queue_type=execution\"")
        utils.runcmd("qmgr -c \"set queue batch started=true\"")
        utils.runcmd("qmgr -c \"set queue batch enabled=true\"")
        utils.runcmd("qmgr -c \"set queue batch resources_default.nodes=1\"")
        utils.runcmd(("qmgr -c \"set queue batch resources_default.walltime="
                      "3600\""))
        utils.runcmd("qmgr -c \"set queue batch max_running = 1\"")
        utils.runcmd("qmgr -c \"set server default_queue=batch\"")

        # Reload configuration
        utils.runcmd("/etc/init.d/pbs_server stop")
        utils.runcmd("/etc/init.d/pbs_server start")

    def post_config(self):
        scratchdir = utils.hiera("scratchdir")
        sessiondir = utils.hiera("sessiondir")

        self._set_control_access(sessiondir, scratchdir)
        self._set_arc_conf(scratchdir)
        self._set_pbs()

    def pre_validate(self):
        utils.install(["myproxy", "nordugrid-arc-client"])


arc_ce = ArcCEDeploy(
    name="arc-ce",
    doc="ARC computing element server deployment.",
    metapkg=["nordugrid-arc-compute-element",
             "torque-server",
             "torque-mom"],
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
    qc_specific_id="arc",
)

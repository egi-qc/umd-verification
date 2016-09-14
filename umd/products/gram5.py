import os
import pwd
import socket
import tempfile

from umd import base
from umd.base.configure import BaseConfig
from umd import config
from umd import system
from umd import utils

exceptions = {
    "known_worldwritable_filelist":
        ["/dev/cpuset/torque/cgroup.event_control",
         "/dev/cpuset/cgroup.event_control"]}


qmgr_conf = """
create queue testq
set queue testq queue_type = Execution
set queue testq resources_max.cput = 48:00:00
set queue testq resources_max.walltime = 72:00:00
set queue testq acl_group_enable = False
set queue testq enabled = True
set queue testq started = True
#
# Set server attributes.
#
set server scheduling = True
set server acl_host_enable = False
set server acl_hosts = %(host)s
set server managers = root@%(host)s
set server operators = root@%(host)s
set server default_queue = testq
set server log_events = 511
set server mail_from = adm
set server query_other_jobs = True
set server scheduler_iteration = 600
set server node_check_rate = 150
set server tcp_timeout = 6
set server node_pack = False
set server mail_domain = never
set server kill_delay = 10
"""


class Gram5Config(BaseConfig):
    def __init__(self):
        super(Gram5Config, self).__init__()

    def torque_config(self):
        if system.distro_version == 'redhat6':
            # ugly hack to get torque installed (SL6)
            utils.runcmd("yum localinstall "
                         "http://mirror.centos.org/centos/6/os/x86_64/"
                         "Packages/hwloc-1.5-3.el6_5.x86_64.rpm")
        utils.install(["torque-server", "torque-scheduler",
                       "torque-mom", "torque-client"])

        # start munge
        utils.runcmd("create-munge-key -f")
        utils.runcmd("service munge restart")

        # PBS does not like the fqdn
        hostname = socket.gethostname()

        TORQUE_VAR = '/var/lib/torque'
        with open(os.path.join(TORQUE_VAR, 'server_name'), 'w+') as f:
            f.write("%s\n" % hostname)
        with open(os.path.join(TORQUE_VAR, 'server_priv', 'nodes'), 'w+') as f:
            f.write("%s np=2\n" % hostname)
        utils.runcmd(
            'sed -i "s/localhost/%s/" %s' %
            (hostname, os.path.join(TORQUE_VAR, 'mom_priv', 'config'))
        )

        # Start torque
        utils.runcmd("service trqauthd restart")
        utils.runcmd("service pbs_server restart")
        utils.runcmd("service pbs_mom restart")
        utils.runcmd("service pbs_sched restart")

        # config queue
        with tempfile.NamedTemporaryFile("w+t", delete=True) as f:
            f.write(qmgr_conf % {'host': hostname})
            f.flush()
            utils.runcmd("qmgr < %s" % f.name)

    def run(self):
        self.torque_config()

        utils.runcmd("chmod 600 /etc/grid-security/hostkey.pem")
        # Start the gatekeeper and add the jobmanagers
        utils.runcmd("service globus-gatekeeper restart")
        utils.runcmd("globus-gatekeeper-admin "
                     "-e jobmanager-fork-poll -n jobmanager")
        utils.runcmd("globus-gatekeeper-admin "
                     "-e jobmanager-pbs-poll -n jobmanager-pbs")
        utils.runcmd("globus-gatekeeper-admin "
                     "-e jobmanager-pbs-seg -n jobmanager-pbs2")

        # Also start the not-polling thing
        utils.runcmd("globus-scheduler-event-generator-admin -e pbs")
        utils.runcmd("service globus-scheduler-event-generator start")

        # Fix the for cpu_per_node count in jobmanager
        utils.runcmd("sed -i -e 's/^cpu_per_node=.*/cpu_per_node=\"2\"/' "
                     "/etc/globus/globus-pbs.conf")
        self.post_config()


class Gram5Deploy(base.Deploy):
    def __init__(self, name, doc=None, metapkg=[], dryrun=False):
        super(Gram5Deploy, self).__init__(name, doc, metapkg, need_cert=True,
                                          has_infomodel=False,
                                          qc_specific_id="gram5",
                                          exceptions=exceptions, dryrun=dryrun)
        config.CFG["cfgtool"] = Gram5Config()
        self.cfgtool = config.CFG["cfgtool"]

    def pre_validate(self):
        # create a user certificate for umd user
        try:
            spasswd = pwd.getpwnam('umd')
        except KeyError:
            utils.runcmd("useradd -m umd")
            spasswd = pwd.getpwnam('umd')
        globus_dir = os.path.join(spasswd[5], '.globus')
        if not os.path.exists(globus_dir):
            os.mkdir(os.path.join(spasswd[5], '.globus'))
            os.chown(globus_dir, spasswd[2], spasswd[3])
        cert_file = os.path.join(globus_dir, 'usercert.pem')
        key_file = os.path.join(globus_dir, 'userkey.pem')
        cert = config.CFG["ca"].issue_cert(hostname="UMD-User",
                                           hash="2048",
                                           key_prv=key_file,
                                           key_pub=cert_file)
        os.chown(cert_file, spasswd[2], spasswd[3])
        os.chown(key_file, spasswd[2], spasswd[3])
        os.chmod(key_file, 0o400)
        os.chmod(cert_file, 0o644)

        # and configure it in the grid-mapfile
        utils.runcmd("echo '%s umd' > /etc/grid-security/grid-mapfile"
                     % cert.subject)


gram5 = Gram5Deploy(
    name="gram5",
    doc="Gram 5 with PBS deployment.",
    metapkg=["globus-gram-job-manager",
             "globus-gram-job-manager-pbs",
             "globus-gram-job-manager-pbs-setup-poll",
             "globus-gram-job-manager-pbs-setup-seg",
             "globus-gram-job-manager-fork",
             "globus-gram-job-manager-fork-setup-poll"],)

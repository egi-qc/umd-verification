import os
import os.path
import re

from umd import api
from umd import config
from umd import system
from umd import utils


def create_fake_proxy(vo="dteam", out="/tmp/umd_proxy"):
    """Creates a fake proxy for further testing.

    :vo: VO used for the proxy creation.
    :out: Output path to store the proxy being created.
    """
    fqdn = system.fqdn
    keypath = "/tmp/userkey.crt"
    certpath = "/tmp/usercert.crt"
    config.CFG["ca"].issue_cert(hostname="perico-palotes",
                                hash="2048",
                                key_prv=keypath,
                                key_pub=certpath)

    utils.runcmd(("voms-proxy-fake -rfc -cert %(certpath)s -key %(keypath)s "
                  "-hours 44000 -voms %(vo)s -hostcert "
                  "/etc/grid-security/hostcert.pem -hostkey "
                  "/etc/grid-security/hostkey.pem "
                  "-fqan /%(vo)s/Role=NULL/Capability=NULL "
                  "-uri %(fqdn)s:15000 -out %(out)s") % locals())
    api.info("Fake proxy created under '%s'" % out)


def add_fake_lsc(vo="dteam", root_dir="/etc/grid-security/vomsdir"):
    """Creates the lsc file for the fake proxy.

    :vo: VO used for adding the LSC entry.
    """
    vo_dir = os.path.join(root_dir, vo)
    if not os.path.exists(vo_dir):
	os.makedirs(vo_dir)

    with open(os.path.join(vo_dir, '.'.join([system.fqdn, "lsc"])), 'a') as f:
        f.write(config.CFG["cert"].subject)
	f.write('\n')
        f.write(config.CFG["ca"].subject)
        f.flush()


def add_openstack_distro_repos(release):
    """Adds the official OpenStack repositories of the distribution.

    :release: OpenStack release.
    """
    def _get_release():
        release_map = {
            "mitaka": ["9\.0\.[0-9]", "9\.1\.[0-9]", "9\.2\.[0-9]"]}
        _release = None
        if release in release_map.keys():
            _release = release
        else:
            for name, regexp in release_map.items():
                for exp in regexp:
                    if re.search(exp, release):
                        return name
        return _release

    matched_release = _get_release()
    if not matched_release:
        api.fail("Could not match OpenStack release: %s" % release,
                 stop_on_error=True)
    if system.distname == "ubuntu":
        utils.enable_repo("cloud-archive:%s" % matched_release)
    elif system.distname == "centos":
        utils.install("centos-release-openstack-%s" % matched_release)

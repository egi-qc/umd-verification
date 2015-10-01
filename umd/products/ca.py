import os.path
import urlparse

from umd import api
from umd import base
from umd.base.installation import Install
from umd import config
from umd import system
from umd import utils


class CADeploy(base.Deploy):
    def pre_install(self):
        if not config.CFG["repository_url"]:
            api.fail("No CA verification URL was given.", stop_on_error=True)

        if system.distname in ["debian", "ubuntu"]:
            repo = "egi-igtf"
            utils.runcmd("wget -q -O - %s | apt-key add -"
                         % os.path.join(config.CFG["repository_url"][0],
                                        "GPG-KEY-EUGridPMA-RPM-3"))
        elif system.distname in ["redhat"]:
            repo = ["EGI-trustanchors", "LCG-trustanchors"]

        utils.remove_repo(repo)

        # FIXME(orviz) workaround CA release with no Debian '.list' repofile
        if system.distname in ["debian", "ubuntu"]:
            # Just one repository is expected
            repo = config.CFG["repository_url"][0]
            ca_version = urlparse.urlparse(repo).path.split("cas/")[-1]
            ca_version = ''.join(ca_version.replace('/', '.', 1).replace('/',
                                                                         '-'))
            repo = os.path.join(repo, '-'.join(["ca-policy-egi-core",
                                               ca_version]))
            repodeb = "deb %s egi-igtf core" % repo

            if system.distro_version == "debian6":
                source = "/etc/apt/sources.list.d/egi-igtf.list"
                utils.runcmd("echo '%s' > %s" % (repodeb, source))
            else:
                utils.runcmd("apt-add-repository '%s'" % repodeb)

    def _install(self, **kwargs):
        # Part of the above workaround
        if system.distname in ["debian", "ubuntu"]:
            kwargs.update({"ignore_repos": True,
                           "ignore_verification_repos": True})
        else:
            kwargs.update({"ignore_repos": True})

        self.pre_install()
        Install().run(**kwargs)
        self.post_install()


ca = CADeploy(
    name="ca",
    doc="CA deployment.",
    metapkg=[
        "ca-policy-egi-core",
        "ca-policy-lcg",
    ],
    qc_step="QC_DIST_1")

crl = base.Deploy(
    name="crl",
    doc="CA/CRL deployment.",
    metapkg=[
        "ca-policy-egi-core",
        "ca-policy-lcg",
        "fetch-crl"],
    qc_specific_id="ca")

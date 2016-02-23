import os.path

from umd import api
from umd import base
from umd.base.installation import Install
from umd import config
from umd import system
from umd import utils


class CADeploy(base.Deploy):
    def pre_install(self):
        # NOTE(orviz) workaround CA release with no Debian '.list' repofile
        if system.distname in ["debian", "ubuntu"]:
            # Just one repository is expected
            repo = "deb %s egi-igtf core" % os.path.join(
        	config.CFG["repository_url"][0],
        	"current")
            utils.remove_repo(repo)
        
            utils.add_repo_key(config.CFG["igtf_repo_key"])
        
            if system.distro_version == "debian6":
        	    source = "/etc/apt/sources.list.d/egi-igtf.list"
        	    utils.runcmd("echo '%s' > %s" % (repo, source))
            else:
        	    utils.enable_repo(repo)
        elif system.distname in ["centos", "redhat"]:
            repo = ["EGI-trustanchors", "LCG-trustanchors"]
            utils.remove_repo(repo)

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

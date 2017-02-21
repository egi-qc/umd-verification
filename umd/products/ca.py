import os.path

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
            repo = "deb %s egi-igtf core" % config.CFG["repository_url"][0]
            utils.remove_repo(repo)

            utils.add_repo_key(config.CFG["igtf_repo_key"])
            print("asfasdfasd: %s" % repo)
            utils.enable_repo(repo)
        elif system.distname in ["centos", "redhat"]:
            repo = ["EGI-trustanchors", "LCG-trustanchors"]
            utils.remove_repo(repo)
            utils.enable_repo(config.CFG["repository_url"][0],
                              name="UMD IGTF verification repo",
                              priority=1)

    def _install(self, **kwargs):
        self.pre_install()
        kwargs.update({"ignore_repos": True,
                       "ignore_verification_repos": True})
        Install().run(**kwargs)
        self.post_install()


ca = CADeploy(
    name="ca",
    doc="CA deployment.",
    metapkg=[
        "ca-policy-egi-core",
        "ca-policy-lcg",
    ],
    # qc_step="QC_DIST_1",
    qc_specific_id="ca")

ca_cam = CADeploy(
    name="ca-cam",
    doc="CA deployment.",
    metapkg=[
        "ca-policy-egi-cam",
    ],
    # qc_step="QC_DIST_1",
    qc_specific_id="ca")

crl = base.Deploy(
    name="crl",
    doc="CA/CRL deployment.",
    metapkg=[
        "ca-policy-egi-core",
        "ca-policy-lcg",
        "fetch-crl"],
    qc_specific_id="ca")

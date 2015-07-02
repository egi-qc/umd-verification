import os.path

from umd.base import Deploy
from umd.base.installation import Install
from umd.base.utils import QCStep
from umd.config import CFG
from umd import system
from umd.utils import info
from umd.utils import get_repos
from umd.utils import install
from umd.utils import runcmd


class CADeploy(Deploy):
    def set_repos(self):
        if system.distname in ["debian", "ubuntu"]:
            verification_repo = ' '.join([
                "deb",
                os.path.join(CFG["repository_url"][0], "current"),
                "egi-igtf",
                "core",
            ])

            if system.distro_version == "ubuntu14":
                 install("software-properties-common")
            #if system.distro_version == "debian6":
            #    install("python-software-properties")

        for repo in get_repos():
            if repo.find("egi-igtf") != -1:
                runcmd("apt-add-repository -r '%s'" % repo)
                info("Repository removed: %s" % repo)

        runcmd("apt-add-repository '%s'" % verification_repo,
               stop_on_error=True)
        info("Repository appended: %s" % verification_repo)

    def pre_install(self):
        if not CFG["repository_url"]:
            qc_step.print_result("FAIL", "No CA verification URL was given.")

        # Set verification CA repository
        self.set_repos()

        # Install UMD release -> contains the pubkey
        runcmd("wget %s -O /tmp/umd_release.deb" % CFG["umd_release"])
        install("/tmp/umd_release.deb")
        runcmd("apt-get update")

    def _install(self, **kwargs):
        kwargs.update({"ignore_repo_config": True})

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

crl = Deploy(
        name="crl",
        doc="CA/CRL deployment.",
        metapkg=[
            "ca-policy-egi-core",
            "ca-policy-lcg",
            "fetch-crl"],
        has_infomodel=False,
        qc_specific_id="ca"
)

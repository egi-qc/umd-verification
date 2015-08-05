import os.path

from umd import api
from umd import base
from umd.base.installation import Install
from umd import config
from umd import system
from umd import utils


class CADeploy(base.Deploy):
    def set_repos(self):
        if system.distname in ["debian", "ubuntu"]:
            verification_repo = ' '.join([
                "deb",
                os.path.join(config.CFG["repository_url"][0], "current"),
                "egi-igtf",
                "core",
            ])

            if system.distro_version == "ubuntu14":
                utils.install("software-properties-common")

        for repo in utils.get_repos():
            if repo.find("egi-igtf") != -1:
                utils.runcmd("apt-add-repository -r '%s'" % repo)
                api.info("Repository removed: %s" % repo)

        utils.runcmd("apt-add-repository '%s'" % verification_repo,
                     stop_on_error=True)
        api.info("Repository appended: %s" % verification_repo)

    def pre_install(self):
        if not config.CFG["repository_url"]:
            api.fail("No CA verification URL was given.")

        # Set verification CA repository
        self.set_repos()

        # Install UMD release -> contains the pubkey
        utils.runcmd("wget %s -O /tmp/umd_release.deb"
                     % config.CFG["umd_release"])
        utils.install("/tmp/umd_release.deb")
        utils.runcmd("apt-get update")

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

crl = base.Deploy(
    name="crl",
    doc="CA/CRL deployment.",
    metapkg=[
        "ca-policy-egi-core",
        "ca-policy-lcg",
        "fetch-crl"],
    has_infomodel=False,
    qc_specific_id="ca")

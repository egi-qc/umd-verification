import os.path

from umd import api
from umd import base
from umd import config
# from umd import products
from umd import system
from umd import utils


class RCDeploy(base.Deploy):
    def _get_metapkg_list(self):
        l = []

        # FIXME The list of products should be gathered programatically
        for pkg in [
            # products.bdii.bdii_site_puppet,
            # products.bdii.bdii_top_puppet,
            # products.fts.fts,
            # products.arc.arc_ce,
            ["dcache", "umd-release"],
        ]:
            if isinstance(pkg, base.Deploy):
                l.extend(pkg.metapkg)
            elif isinstance(pkg, list):
                l.extend(pkg)
            else:
                l.append(pkg)
        api.info("Release candidate will install the following products: %s"
                 % l)

        return l

    def pre_install(self):
        utils.enable_repo(config.CFG["repository_url"], name="UMD base RC")
        # Add IGTF repository as well (some products have dependencies on it)
        utils.enable_repo(config.CFG["igtf_repo"])
        # Get all the (meta)packages to be installed
        config.CFG["metapkg"] = self._get_metapkg_list()

    def _install(self, **kwargs):
        kwargs.update({
            "ignore_repos": True,
            "ignore_verification_repos": True})

        self.pre_install()
        base.installation.Install().run(**kwargs)
        self.post_install()


rc = RCDeploy(
    name="release-candidate",
    doc="Release Candidate probe.",
    qc_step="QC_DIST_1",
)

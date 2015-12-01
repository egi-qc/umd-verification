import itertools
import os.path

from umd import api
from umd import base
from umd import config
# from umd import products
from umd import system


class RCDeploy(base.Deploy):
    def _get_metapkg_list(self):
        l = []

        # FIXME The list of products should be gathered programatically
        for pkg in itertools.chain(
            # products.storm.sl6.metapkg,
            # products.ui.ui_gfal.metapkg,
            # products.globus.gridftp.metapkg,
            # products.gram5.gram5.metapkg,
            ["dcache"],
        ):
            if isinstance(pkg, list):
                l.extend(pkg)
            else:
                l.append(pkg)
        api.info("Release candidate will install the following products: %s"
                 % l)

        return l

    def pre_install(self):
        repo_id = {
            "redhat6": "sl6",
            "redhat5": "sl5",
        }
        config.CFG["repository_url"] = [os.path.join(
            config.CFG["repository_url"][0],
            "repofiles/%s/" % repo_id[system.distro_version])]
        api.info("Changing repository URL to %s"
                 % config.CFG["repository_url"][0])

        config.CFG["metapkg"] = self._get_metapkg_list()


rc = RCDeploy(
    name="release-candidate",
    doc="Release Candidate probe.",
    qc_step="QC_DIST_1",
)

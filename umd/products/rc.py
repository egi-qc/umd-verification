import os.path

from umd import api
from umd import base
from umd import config
from umd import system


class RCDeploy(base.Deploy):
    # FIXME This should be obtained programatically
    def _get_metapkg_list(self):
        l = []
        for pkg in ["dcache"]:
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
    dryrun=True)

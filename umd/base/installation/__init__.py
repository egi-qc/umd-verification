import os.path
import shutil

from umd import api
from umd.base import utils as butils
from umd import config
from umd import exception
from umd import system
from umd import utils


class Install(object):
    def __init__(self):
        self.pkgtool = utils.PkgTool()
        self.metapkg = config.CFG["metapkg"]

    def _enable_verification_repo(self,
                                  qc_step,
                                  url,
                                  download_dir="/tmp/repofiles"):
        """Downloads the repofiles found in the given URL."""
        qc_step.runcmd("rm -rf %s/*" % download_dir, fail_check=False)
        qc_step.runcmd("wget -P %s -r --no-parent -R*.html* %s"
                       % (download_dir, url),
                       fail_check=False,
                       stop_on_error=False)
        repofiles = []
        for path in os.walk(download_dir):
            if path[2] and path[0].find(self.pkgtool.get_repodir()) != -1:
                for f in path[2]:
                    if f.endswith(self.pkgtool.get_extension()):
                        repofiles.append(os.path.join(path[0], f))
        if repofiles:
            repopath = self.pkgtool.get_path()
            for f in repofiles:
                repofile = os.path.basename(f)
                shutil.copy2(f, os.path.join(repopath, repofile))
                api.info("Verification repository '%s' enabled." % repofile)

        else:
            qc_step.print_result("FAIL",
                                 ("Could not find any valid %s "
                                  "('%s') file in the remote repository URL")
                                 % (system.distname,
                                    self.pkgtool.get_extension()),
                                 do_abort=True)

    def _check(self):
        if not self.metapkg:
            api.fail("No metapackage selected", stop_on_error=True)

    def run(self, **kwargs):
        """Runs UMD installation."""
        self._check()

        # Handle installation type
        installation_type = config.CFG["installation_type"]
        if installation_type == "update":
            qc_step = butils.QCStep("QC_UPGRADE_1",
                                    "Upgrade",
                                    "qc_upgrade_1")
        elif installation_type == "install":
            qc_step = butils.QCStep("QC_DIST_1",
                                    "Binary Distribution",
                                    "qc_inst_1")

        repo_config = True
        if "ignore_repos" in kwargs.keys():
            repo_config = False

        verification_repo_config = True
        if "ignore_verification_repos" in kwargs.keys():
            verification_repo_config = False

        if repo_config:
            # Distribution-based settings
            repopath = self.pkgtool.client.path
            msg_purge = "UMD"
            paths_to_purge = ["%s/UMD-*" % repopath]
            pkgs_to_purge = ["umd-release*"]
            pkgs_to_download = [("UMD", config.CFG["umd_release"])]
            pkgs_additional = []
            if system.distname == "redhat":
                msg_purge = " ".join(["EPEL and/or", msg_purge])
                paths_to_purge.insert(0, "%s/epel-*" % repopath)
                pkgs_to_purge.insert(0, "epel-release*")
                pkgs_to_download.insert(0, ("EPEL",
                                            config.CFG["epel_release"]))
                pkgs_additional.append("yum-priorities")

            # Installation/upgrade workflow
            r = self.pkgtool.remove(pkgs_to_purge)
            if r.failed:
                api.info("Could not delete %s release packages." % msg_purge)

            if qc_step.runcmd("/bin/rm -f %s" % " ".join(paths_to_purge)):
                api.info("Purged any previous %s repository file." % msg_purge)

            for pkg in pkgs_to_download:
                pkg_id, pkg_url = pkg
                if pkg_url:
                    pkg_base = os.path.basename(pkg_url)
                    pkg_loc = os.path.join("/tmp", pkg_base)
                    if qc_step.runcmd("wget %s -O %s" % (pkg_url, pkg_loc)):
                        api.info("%s release package fetched from %s."
                                 % (pkg_id, pkg_url))

                    r = self.pkgtool.install(pkg_loc)
                    if r.failed:
                        qc_step.print_result("FAIL",
                                             ("Error while installing %s "
                                              "release.") % pkg_id)
                    else:
                        api.info("%s release package installed." % pkg_id)

            for pkg in pkgs_additional:
                r = self.pkgtool.install(pkg)
                if r.failed:
                    api.info("Error while installing '%s'." % pkg)
                else:
                    api.info("'%s' requirement installed." % pkg)

        if config.CFG["dryrun"]:
            api.info(("Installation or upgrade process will be simulated "
                      "(dryrun: ON)"))
            self.pkgtool.dryrun = True

        if installation_type == "update":
            if config.CFG["repository_url"]:
                # 1) Install base (production) version
                r = self.pkgtool.install(self.metapkg)
                if r.failed:
                    api.fail(("Could not install base (production) version of "
                              "metapackage '%s'" % self.metapkg),
                             stop_on_error=True)
                else:
                    api.info("UMD product/s '%s' production version installed."
                             % self.metapkg)

                # 2) Enable verification repository
                if verification_repo_config:
                    for url in config.CFG["repository_url"]:
                        self._enable_verification_repo(qc_step, url)

                # 3) Refresh
                self.pkgtool.refresh()

            # 4) Update
            api.info("Using repositories: %s" % self.pkgtool.get_repos())
            r = self.pkgtool.update()
            if r.failed:
                api.fail("Metapackage '%s' update failed." % self.metapkg,
                         stop_on_error=True)
            d = self.pkgtool.get_pkglist(r)

        elif installation_type == "install":
            # 1) Enable verification repository
            if verification_repo_config:
                for url in config.CFG["repository_url"]:
                    self._enable_verification_repo(qc_step, url)

            # 2) Refresh
            self.pkgtool.refresh()

            # 3) Install verification version
            api.info("Using repositories: %s" % self.pkgtool.get_repos())
            r = self.pkgtool.install(self.metapkg)
            if r.failed:
                api.fail("Metapackage '%s' installation failed.",
                         stop_on_error=True)
            d = self.pkgtool.get_pkglist(r)

            # NOTE(orviz): missing WARNING case
        else:
            raise exception.InstallException(("Installation type '%s' "
                                              "not implemented."
                                              % installation_type))

        is_ok = True
        # r.stderr
        if r.failed:
            # FIXME (should be within YUM class) YUM's downloadonly
            # plugin returns 1 on success
            if r.stderr.find("--downloadonly specified") != -1:
                is_ok = True
                msgtext = "Dry-run installation ended successfully."
            else:
                is_ok = False
                msgtext = r.msgerror
        else:
            msgtext = "Installation ended successfully."

        if is_ok:
            if self.metapkg:
                for pkg in self.metapkg:
                    try:
                        api.info("Package '%s' installed version: %s."
                                 % (pkg, d[pkg]))
                    except KeyError:
                        api.fail("Package '%s' could not be installed." % pkg)
                        is_ok = False
                        msgtext = "Not all the packages could be installed."
            else:
                api.info("List of packages updated: %s"
                         % self.pkgtool.get_pkglist(r))

        if is_ok:
            qc_step.print_result("OK", msgtext)
        else:
            qc_step.print_result("FAIL", msgtext, do_abort=True)

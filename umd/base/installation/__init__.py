import os.path
import shutil

from umd.api import info
from umd.api import fail
from umd.config import CFG
from umd import exception
from umd.base.utils import QCStep
from umd import system
from umd.utils import PkgTool


class Install(object):
    def __init__(self):
        self.pkgtool = PkgTool()
        self.metapkg = CFG["metapkg"]

    def _enable_verification_repo(self,
                                  qc_step,
                                  url,
                                  download_dir="/tmp/repofiles"):
        """Downloads the repofiles found in the given URL."""
        qc_step.runcmd("rm -rf %s/*" % download_dir, fail_check=False)
        r = qc_step.runcmd("wget -P %s -r -l1 --no-parent -R*.html* %s"
                           % (download_dir, url))
        if r.failed:
            qc_step.print_result("FAIL",
                                 "Error retrieving verification repofile.",
                                 do_abort=True)

        repofiles = []
        for path in os.walk(download_dir):
            if path[2] and path[0].find("repofiles") != -1:
                for f in path[2]:
                    if not f.endswith(".repo"):
                        info("File without '.repo' extension found: '%s'" % f)
                    else:
                        repofiles.append(os.path.join(path[0], f))
        if repofiles:
            repopath = self.pkgtool.get_path()
            for f in repofiles:
                repofile = os.path.basename(f)
                shutil.copy2(f, os.path.join(repopath, repofile))
                info("Verification repository '%s' enabled." % f)

    def run(self, **kwargs):
        """Runs UMD installation."""
        # Handle installation type
        installation_type = CFG["installation_type"]
        if installation_type == "update":
            qc_step = QCStep("QC_UPGRADE_1", "Upgrade", "/tmp/qc_upgrade_1")
        elif installation_type == "install":
            qc_step = QCStep("QC_DIST_1",
                             "Binary Distribution",
                             "/tmp/qc_inst_1")

        repo_config = True
        if "ignore_repo_config" in kwargs.keys():
            repo_config = False

        if repo_config:
            # Distribution-based settings
            repopath = self.pkgtool.client.path
            msg_purge = "UMD"
            paths_to_purge = ["%s/UMD-*" % repopath]
            pkgs_to_purge = ["umd-release*"]
            pkgs_to_download = [("UMD", CFG["umd_release"])]
            pkgs_additional = []
            if system.distname == "redhat":
                msg_purge = " ".join(["EPEL and/or", msg_purge])
                paths_to_purge.insert(0, "%s/epel-*" % repopath)
                pkgs_to_purge.insert(0, "epel-release*")
                pkgs_to_download.insert(0, ("EPEL", CFG["epel_release"]))
                pkgs_additional.append("yum-priorities")

            # Installation/upgrade workflow
            r = qc_step.runcmd(self.pkgtool.remove(pkgs_to_purge),
                               stop_on_error=False)
            if r.failed:
                info("Could not delete %s release packages." % msg_purge)

            if qc_step.runcmd("/bin/rm -f %s" % " ".join(paths_to_purge)):
                info("Purged any previous %s repository file." % msg_purge)

            for pkg in pkgs_to_download:
                pkg_id, pkg_url = pkg
                pkg_base = os.path.basename(pkg_url)
                pkg_loc = os.path.join("/tmp", pkg_base)
                if qc_step.runcmd("wget %s -O %s" % (pkg_url, pkg_loc)):
                    info("%s release package fetched from %s." % (pkg_id, pkg_url))

                r = qc_step.runcmd(self.pkgtool.install(pkg_loc))
                if r.failed:
                    qc_step.print_result("FAIL",
                                         "Error while installing %s release."
                                         % pkg_id)
                else:
                    info("%s release package installed." % pkg_id)

            for pkg in pkgs_additional:
                r = qc_step.runcmd(self.pkgtool.install(pkg))
                if r.failed:
                    info("Error while installing '%s'." % pkg)
                else:
                    info("'%s' requirement installed." % pkg)

        # Refresh repositories
        qc_step.runcmd(self.pkgtool.refresh())

        if CFG["dryrun"]:
            info(("Installation or upgrade process will be simulated "
                  "(dryrun: ON)"))
            self.pkgtool.dryrun = True

        if installation_type == "update":
            if CFG["repository_url"]:
                # 1) Install base (production) version
                r = qc_step.runcmd(self.pkgtool.install(self.metapkg))
                if not r.failed:
                    info("UMD product/s '%s' production version installed."
                         % self.metapkg)

                # 2) Enable verification repository
                for url in CFG["repository_url"]:
                    self._enable_verification_repo(qc_step, url)
                    info("Verification repository '%s' enabled." % url)

            # 3) Update
            r = qc_step.runcmd(self.pkgtool.update(),
                               fail_check=False,
                               stop_on_error=False,
                               get_error_msg=True)
            d = self.pkgtool.get_pkglist(r)

        elif installation_type == "install":
            # 1) Enable verification repository
            for url in CFG["repository_url"]:
                self._enable_verification_repo(qc_step, url)
                info("Verification repository '%s' enabled." % url)

            # 2) Install verification version
            r = qc_step.runcmd(self.pkgtool.install(self.metapkg),
                               fail_check=False,
                               stop_on_error=False,
                               get_error_msg=True)
            d = self.pkgtool.get_pkglist(r)

            # NOTE(orviz): missing WARNING case
        else:
            raise exception.InstallException(("Installation type '%s' "
                                              "not implemented."
                                              % installation_type))
        is_ok = True
        if r.failed:
            # YUM's downloadonly plugin returns 1 on success
            if r.stderr.find("--downloadonly specified") != 1:
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
                        info("Package '%s' installed version: %s." % (pkg, d[pkg]))
                    except KeyError:
                        fail("Package '%s' could not be installed." % pkg)
                        is_ok = False
                        msgtext = "Not all the packages could be installed."
            else:
                info("List of packages updated: %s" % self.pkgtool.get_pkglist(r))

        if is_ok:
            qc_step.print_result("OK", msgtext)
        else:
            qc_step.print_result("FAIL", msgtext)

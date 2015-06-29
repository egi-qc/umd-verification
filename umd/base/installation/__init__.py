import os.path
import shutil

from umd.api import info
from umd.config import CFG
from umd import exception
from umd.base.utils import QCStep
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
        installation_type = CFG["installation_type"]
        if installation_type == "update":
            qc_step = QCStep("QC_UPGRADE_1", "Upgrade", "/tmp/qc_upgrade_1")
        elif installation_type == "install":
            qc_step = QCStep("QC_INST_1",
                             "Binary Distribution",
                             "/tmp/qc_inst_1")

        r = qc_step.runcmd(self.pkgtool.remove(["epel-release*",
                                                "umd-release*"]))
        if r.failed:
            info("Could not delete [epel/umd]-release packages.")

        if qc_step.runcmd(("/bin/rm -f /etc/yum.repos.d/UMD-* "
                           "/etc/yum.repos.d/epel-*")):
            info(("Purged any previous EPEL or UMD repository file."))

        for pkg in (("EPEL", CFG["epel_release"]),
                    ("UMD", CFG["umd_release"])):
            pkg_id, pkg_url = pkg
            pkg_base = os.path.basename(pkg_url)
            pkg_loc = os.path.join("/tmp", pkg_base)
            if qc_step.runcmd("wget %s -O %s" % (pkg_url, pkg_loc)):
                info("%s release RPM fetched from %s." % (pkg_id, pkg_url))

            r = qc_step.runcmd(self.pkgtool.install(pkg_loc))
            if r.failed:
                qc_step.print_result("FAIL",
                                     "Error while installing %s release."
                                     % pkg_id)
            else:
                info("%s release package installed." % pkg_id)

        r = qc_step.runcmd(self.pkgtool.install("yum-priorities"))
        if r.failed:
            info("Error while installing 'yum-priorities'.")
        else:
            info("'yum-priorities' (UMD) requirement installed.")

        if installation_type == "update":
            # 1) Install base (production) version
            r = qc_step.runcmd(self.pkgtool.install(self.metapkg))
            if not r.failed:
                info("UMD product/s '%s' installation finished."
                     % self.metapkg)

            # 2) Enable verification repository
            for url in CFG["repository_url"]:
                self._enable_verification_repo(qc_step, url)
                info("Verification repository '%s' enabled." % url)

            # 3) Update
            r = qc_step.runcmd(self.pkgtool.update())
            if not r.failed:
                qc_step.print_result("OK",
                                     msg="System successfully updated.")
        elif installation_type == "install":
            # 1) Enable verification repository
            for url in CFG["repository_url"]:
                self._enable_verification_repo(qc_step, url)
                info("Verification repository '%s' enabled." % url)

            # 2) Install verification version
            r = qc_step.runcmd(self.pkgtool.install(self.metapkg))
            # NOTE(orviz): missing WARNING case
            if not r.failed:
                qc_step.print_result("OK",
                                     ("Metapackage '%s' installed "
                                      "successfully.." % self.metapkg))
        else:
            raise exception.InstallException(("Installation type '%s' "
                                              "not implemented."
                                              % installation_type))

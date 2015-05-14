import os.path
import shutil

from umd.api import info
from umd import exception
from umd.base.utils import QCStep
from umd.utils import PkgTool


class Install(object):
    def __init__(self, metapkg):
        self.pkgtool = PkgTool()
        self.metapkg = metapkg

    def _enable_verification_repo(self,
                                  qc_step,
                                  repository_url,
                                  download_dir="/tmp/repofiles"):
        """Downloads the repofiles found in the given URL.

           Note: repofiles can be found (typo?) without the ".repo" extension.
        """
        qc_step.runcmd("rm -rf %s/*" % download_dir, fail_check=False)
        r = qc_step.runcmd("wget -P %s -r -l1 --no-parent -R*.html* %s"
                           % (download_dir,
                              os.path.join(repository_url, "repofiles")))
        if r.failed:
            qc_step.print_result("FAIL",
                                 "Error retrieving verification repofile.",
                                 do_abort=True)

        repofiles = []
        for path in os.walk(download_dir):
            if os.path.basename(path[0]) == "repofiles":
                if path[-1]:
                    repofiles.extend([os.path.join(path[0], f)
                                      for f in path[-1]])
        if repofiles:
            repopath = self.pkgtool.get_path()
            for f in repofiles:
                repofile = os.path.basename(f)
                if not repofile.endswith(".repo"):
                    repofile = '.'.join([repofile, "repo"])
                shutil.copy2(f, os.path.join(repopath, repofile))
                info("Verification repository '%s' enabled." % repofile)

    def run(self,
            installation_type,
            epel_release_url,
            umd_release_url,
            repository_url=[],
            **kwargs):
        """Runs UMD installation.

           Arguments::
                installation_type: install from scratch ('install') or
                                   update ('update')
                epel_release_url: EPEL release (URL).
                umd_release_url : UMD release (URL).
                repository_url: verification repository URL (multiple allowed).
        """
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

        for pkg in (("EPEL", epel_release_url),
                    ("UMD", umd_release_url)):
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
            for url in repository_url:
                self._enable_verification_repo(qc_step, url)
                info("Verification repository '%s' enabled." % url)

            # 3) Update
            r = qc_step.runcmd(self.pkgtool.update())
            if not r.failed:
                qc_step.print_result("OK",
                                     msg="System successfully updated.")
        elif installation_type == "install":
            # 1) Enable verification repository
            for url in repository_url:
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

import os.path
import shutil

from umd import api
from umd.common import qc
from umd import config
from umd import exception
from umd import system
from umd import utils


class Install(object):
    def __init__(self):
        self.pkgtool = utils.PkgTool()
        self.metapkg = config.CFG["metapkg"]
        self.download_dir = "/tmp/repofiles"
        self.repo_config = True
        self.verification_repo_config = True
        self.repo_url = config.CFG.get("repository_url", [])
        self.repo_file = config.CFG.get("repository_file", [])

    def _enable_verification_repo(self,
                                  url,
                                  logfile,
                                  name=None,
                                  is_file=False):
        """Downloads the repofiles found in the given URL."""
        repopath = self.pkgtool.get_path()

        if is_file:
            dest = os.path.join(repopath, os.path.basename(url))
            cmd = "wget %s -O %s" % (url, dest)
            utils.runcmd(cmd, log_to_file=logfile)
            api.info("Repository file downloaded to %s" % dest)
        else:
            utils.runcmd("rm -rf %s/*" % self.download_dir)

            cmd = ("wget -P %s -r --no-parent -R*.html* "
                   "%s") % (self.download_dir, url)
            if url.startswith("https"):
                cmd = ' '.join([cmd, "--no-check-certificate"])
                self.pkgtool.handle_repo_ssl()

            r = utils.runcmd(cmd, log_to_file=logfile)
            if r.failed:
                api.fail("Could not fetch repository '%s'" % url,
                         logfile=r.logfile)

            repofiles = utils.find_extension_files(
                self.download_dir,
                self.pkgtool.get_extension())
            if repofiles:
                for f in repofiles:
                    repofile = os.path.basename(f)
                    shutil.copy2(f, os.path.join(repopath, repofile))
                    api.info("Verification repository '%s' enabled."
                             % repofile)

            else:
                api.info(("Could not find any %s ('%s') repository file at %s "
                          "repository URL") % (system.distname,
                                               self.pkgtool.get_extension(),
                                               url))
                utils.enable_repo(url, name=name)

    def _get_pkgs_from_verification_repo(self):
        d = {}
        pkg_files = utils.find_extension_files(
            self.download_dir,
            self.pkgtool.get_pkg_extension())
        for f in pkg_files:
            try:
                name, version = self.pkgtool.get_pkg_version(
                    f,
                    check_installed=False).items()[0]
                d[name] = '-'.join([name, version])
            except IndexError:
                api.fail("Malformed or empty package: %s" % f,
                         stop_on_error=True)
        return d

    def _show_pkg_version(self, d_pkg):
        """Shows installed version of packages from the verification repo.

        :d_pkg: dict containing installed package specs (name, version).
        """
        d = self._get_pkgs_from_verification_repo()

        for name, pkg in d.items():
            try:
                installed_pkg = d_pkg["name"]
                if pkg == installed_pkg:
                    api.info("Package '%s' installed version: '%s'" % (name,
                                                                       pkg))
                else:
                    api.info(("Package '%s' installed version (%s) does not "
                              "match verification repository version: %s"
                              % (name, installed_pkg, pkg)))
            except KeyError:
                _pkgs = self.pkgtool.get_pkg_version(name,
                                                     check_installed=True)
                if _pkgs:
                    for _name, _pkg in _pkgs.items():
                        if not isinstance(_pkg, list):
                            _pkg = [_pkg]
                        for _p in _pkg:
                            api.info("'%s' installed version: '%s'" % (_name,
                                                                       _p))
                else:
                    api.info("'%s' not installed" % name)

    def _check(self):
        if not self.metapkg:
            api.fail("No metapackage selected", stop_on_error=True)

    def _distro_pkgs(self, logfile):
        pkgs = []
        if system.distname == "redhat":
            pkgs.append("yum-priorities")
            pkgs.append("yum-conf-sl%sx" % system.version_major)

        for pkg in pkgs:
            r = self.pkgtool.install(pkg, log_to_file=logfile)
            if r.failed:
                api.fail("Error while installing '%s'." % pkg,
                         logfile=r.logfile)
            else:
                api.info("'%s' requirement installed." % pkg)

    def _repo_pkgs(self, logfile):
        # Distribution-based settings
        repopath = self.pkgtool.client.path
        msg_purge = "UMD"
        paths_to_purge = ["%s/UMD-*" % repopath]
        pkgs_to_purge = ["umd-release*"]
        pkgs_to_download = [("UMD", config.CFG["umd_release_pkg"])]
        if system.distname == "redhat":
            msg_purge = " ".join(["EPEL and/or", msg_purge])
            paths_to_purge.insert(0, "%s/epel-*" % repopath)
            pkgs_to_purge.insert(0, "epel-release*")
            pkgs_to_download.insert(0, ("EPEL",
                                        config.CFG["epel_release"]))

        # Remove any trace of UMD (and external) repository files
        r = self.pkgtool.remove(pkgs_to_purge, stop_on_error=False)
        if r.failed:
            api.info("Could not delete %s release packages." % msg_purge)

        if utils.runcmd("/bin/rm -f %s" % " ".join(paths_to_purge)):
            api.info("Purged any previous %s repository file." % msg_purge)

        # Import repository keys
        if config.CFG["repo_keys"]:
            self.pkgtool.add_repo_key(config.CFG["repo_keys"])

        # Install UMD (and external) realease packages
        for pkg in pkgs_to_download:
            pkg_id, pkg_url = pkg
            if pkg_url:
                pkg_base = os.path.basename(pkg_url)
                pkg_loc = os.path.join("/tmp", pkg_base)
                r = utils.runcmd("wget %s -O %s" % (pkg_url, pkg_loc),
                                 log_to_file=logfile)
                if r.failed:
                    api.fail("Could not fetch %s release package from %s"
                             % (pkg_id, pkg_url),
                             logfile=r.logfile,
                             stop_on_error=True)
                else:
                    api.info("%s release package fetched from %s"
                             % (pkg_id, pkg_url))

                r = self.pkgtool.install(pkg_loc, log_to_file=logfile)
                if r.failed:
                    api.fail("Error while installing %s release." % pkg_id,
                             logfile=r.logfile,
                             stop_on_error=True)
                else:
                    api.info("%s release package installed." % pkg_id)

    def _handle_output_msg(self, r, d):
        is_ok = True
        # r.stderr
        if r.failed or not r.succeeded:
            # NOTE (should be within YUM class) YUM's downloadonly
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
                d_repos_from_pkg = self.pkgtool.get_repo_from_pkg(d.keys())
                for pkg in self.metapkg:
                    # APT can include specific versioning with '='
                    pkg = pkg.split('=')[0]
                    try:
                        if pkg in d_repos_from_pkg.keys():
                            api.info(("Metapackage '%s' installed version: %s"
                                      " - %s" % (pkg,
                                                 d[pkg],
                                                 d_repos_from_pkg[pkg])))
                    except KeyError:
                        api.fail("Package '%s' could not be installed." % pkg)
                        is_ok = False
                        msgtext = "Not all the packages could be installed."
            else:
                api.info("List of packages updated: %s"
                         % self.pkgtool.get_pkglist(r))

        if is_ok:
            api.ok(msgtext)
        else:
            api.fail(msgtext, logfile=r.logfile, stop_on_error=True)

    def _handle_repo_adding(self, repo, logfile, is_file=False):
        """Handles repository adding.

        :is_file: The given URL matches a repository file (.list, .repo).
        """
        if repo:
            if is_file:
                api.info("Repository files found: adding")
            else:
                api.info("Repository URLs found: adding")
            if self.verification_repo_config:
                c = 1
                for url in repo:
                    self._enable_verification_repo(
                        url,
                        logfile=logfile,
                        name="fab_added_repository_%s" % c,
                        is_file=is_file)
                    c += 1

    @qc.qcstep("QC_DIST_1", "Binary Distribution")
    def qc_dist_1(self):
        _logfile = "qc_inst_1"

        if self.repo_config:
            self._repo_pkgs(logfile=_logfile)
        self._distro_pkgs(logfile=_logfile)
        # FIXME(orviz) hack: UMD4 base for SL6 does not exist!
        if (system.distro_version == "redhat6" and
           config.CFG["umd_release"] == "4"):
                self.pkgtool.disable_repo("UMD-4-base")

        # 1) Enable verification repositories
        self._handle_repo_adding(self.repo_url, _logfile)
        self._handle_repo_adding(self.repo_file, _logfile, is_file=True)

        # 2) Refresh
        self.pkgtool.refresh()

        # 3) Install verification version
        api.info("Using repositories: %s" % self.pkgtool.get_repos())
        return utils.install(self.metapkg, log_to_file=_logfile)

    @qc.qcstep("QC_UPGRADE_1", "Upgrade")
    def qc_upgrade_1(self):
        _logfile = "qc_upgrade_1"

        if self.repo_config:
            self._config_repo(logfile=_logfile)
        self._distro_pkgs(logfile=_logfile)
        # FIXME(orviz) hack: UMD4 base for SL6 does not exist!
        if (system.distro_version == "redhat6" and
           config.CFG["umd_release"] == "4"):
                self.pkgtool.disable_repo("UMD-4-base")

        # 1) Install base (production) version
        r = self.pkgtool.install(self.metapkg, log_to_file=_logfile)
        if r.failed:
            api.fail(("Could not install base (production) version of "
                      "metapackage '%s'" % self.metapkg),
                     logfile=r.logfile,
                     stop_on_error=True)
        else:
            api.info("UMD product/s '%s' production version installed."
                     % self.metapkg)

        # 2) Enable verification repository
        self._handle_repo_adding(self.repo_url, _logfile)
        self._handle_repo_adding(self.repo_file, _logfile, is_file=True)

        # 3) Refresh
        self.pkgtool.refresh()

        # 4) Update
        api.info("Using repositories: %s" % self.pkgtool.get_repos())
        return self.pkgtool.update(log_to_file=_logfile)

    def run(self, **kwargs):
        """Runs UMD installation."""
        self._check()

        if "ignore_repos" in kwargs.keys():
            self.repo_config = False

        if "ignore_verification_repos" in kwargs.keys():
            self.verification_repo_config = False

        if config.CFG["dryrun"]:
            api.info(("Installation or upgrade process will be simulated "
                      "(dryrun: ON)"))
            self.pkgtool.dryrun = True

        # Handle installation type
        installation_type = config.CFG["installation_type"]
        if installation_type == "update":
            r = self.qc_upgrade_1()
        elif installation_type == "install":
            r = self.qc_dist_1()
        else:
            raise exception.InstallException(("Installation type '%s' "
                                              "not implemented."))
        # Manage output
        d = {}
        if r.failed or not r.succeeded:
            r.msgerror = "Metapackage '%s' installation failed." % self.metapkg
        else:
            # Get list of (name, version) installed packages
            d = self.pkgtool.get_pkglist(r)

            # Show package version
            self._show_pkg_version(d)

        self._handle_output_msg(r, d)

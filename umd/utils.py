import inspect
import os
import os.path
import re
import tempfile

import fabric
from fabric import api as fabric_api
from fabric import colors

from umd import api
from umd import config
from umd import exception
from umd import system


def to_list(obj):
    if not isinstance(obj, (str, list, tuple)):
        raise exception.ConfigException("obj variable type '%s' not supported."
                                        % type(obj))
    elif isinstance(obj, (str, tuple)):
        return [obj]
    return obj


def to_file(r, logfile):
    """Writes Fabric capture result to the given file."""
    def _write(fname, msg):
        dirname = os.path.dirname(fname)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
            api.info("Log directory '%s' has been created." % dirname)
        with open(fname, 'a') as f:
            f.write(msg)
            f.flush()

    l = []
    try:
        if r.stdout:
            _fname = '.'.join([logfile, "stdout"])
            _write(_fname, r.stdout)
            l.append(_fname)
        if r.stderr:
            _fname = '.'.join([logfile, "stderr"])
            _write(_fname, r.stderr)
            l.append(_fname)
    except AttributeError:
        if isinstance(r, str):
            _fname = '.'.join([logfile, "stdout"])
            _write(_fname, r)
            l.append(_fname)
    return l


def format_error_msg(logs, cmd=None):
    msg_l = []
    if logs:
        msg_l.append("See more information in logs (%s)." % ','.join(logs))
    if cmd:
        msg_l.append("Error while executing command '%s'." % cmd)

    return ' '.join(msg_l)


def runcmd(cmd,
           chdir=None,
           fail_check=True,
           stop_on_error=False,
           logfile=None,
           get_error_msg=False,
           stderr_to_stdout=False):
    """Runs a generic command.

            cmd: command to execute.
            chdir: local directory to run the command from.
            fail_check: boolean that indicates if the workflow must be
                interrupted in case of failure.
            stop_on_error: whether abort or not in case of failure.
            logfile: file to log the command execution.
            get_error_msg: return the formatted error message.
            stderr_to_stdout: redirect standard error to standard output.
    """
    if stderr_to_stdout:
        cmd = ' '.join([cmd, "2>&1"])

    if chdir:
        with fabric.context_managers.lcd(chdir):
            with fabric_api.settings(warn_only=True):
                r = fabric_api.local(cmd, capture=True)
    else:
        with fabric_api.settings(warn_only=True):
            r = fabric_api.local(cmd, capture=True)

    logs = []
    if logfile:
        logs = to_file(r, logfile)
    if logs:
        r.logfile = logs

    if fail_check and r.failed:
        msg = format_error_msg(logs, cmd)
        if stop_on_error:
            fabric_api.abort(api.fail(msg))
        else:
            api.fail(msg)
        if get_error_msg:
            # if not msg:
            #     debug("No message was created for command '%s'" % cmd)
            r.msgerror = msg

    return r


class Yum(object):
    def __init__(self):
        self.path = "/etc/yum.repos.d/"
        self.extension = ".repo"
        self.repodir = "repofiles"

    def run(self, action, dryrun, pkgs=None):
        opts = ''
        if dryrun:
            if system.distro_version == "redhat5":
                runcmd("yum -y install yum-downloadonly")
            elif system.distro_version == "redhat6":
                runcmd("yum -y install yum-plugin-downloadonly")
            opts = "--downloadonly"

        if action == "refresh":
            action = "makecache"

        if pkgs:
            return "yum -y %s %s %s" % (opts, action, " ".join(pkgs))
        else:
            return "yum -y %s %s" % (opts, action)

    def get_pkglist(self, r):
        """Gets the list of packages being installed parsing yum output."""
        d = {}
        for line in filter(None, r.stdout.split('=')):
            if line.startswith("\nInstalling:\n"):
                for line2 in line.split('\n'):
                    try:
                        name, arch, version, repo, size, unit = line2.split()
                        d[name] = '.'.join(['-'.join([name, version]), arch])
                    except ValueError:
                        pass

        # YUM: last version installed
        for line in r.stdout.split('\n'):
            m = re.search("Package (.+) already installed and latest version",
                          line)
            if m:
                all = ' '.join(m.groups())
                name = re.search("([a-zA-Z0-9-_]+)-\d+.+", all).groups()[0]
                d[name] = ' '.join([all, "(already installed)"])

        return d

    def get_repos(self):
        l = []
        is_repo = False
        for line in runcmd("yum repolist").split('\n'):
            l_str = filter(None, line.split('  '))
            if "repo id" in l_str:
                is_repo = True
                continue
            try:
                if l_str[0].startswith("repolist"):
                    is_repo = False
                    continue
            except IndexError:
                pass
            if is_repo:
                l.append(l_str[0])
        return l

    def remove_repo(self, repolist):
        """Remove all the appearances of a list of repositories.

        :repolist: list of repository names (ID between brackets)
        """
        for repo in repolist:
            r = runcmd("grep %s %s/* | cut -d':' -f1|uniq" % (repo, self.path))
            if r:
                for f in r.split('\n'):
                    os.remove(f)
                    api.info("Existing repository '%s' removed." % f)


class Apt(object):
    def __init__(self):
        self.path = "/etc/apt/sources.list.d/"
        self.extension = ".list"
        # FIXME this is not right
        self.repodir = "repo-files"

    def run(self, action, dryrun, pkgs=None):
        if pkgs:
            if os.path.exists(pkgs[0]):
                return "dpkg -i %s" % " ".join(pkgs)

        opts = ''
        if dryrun:
            opts = "--dry-run"

        if action == "refresh":
            action = "update"

        if pkgs:
            return "apt-get -y %s %s %s" % (opts, action, " ".join(pkgs))
        else:
            return "apt-get -y %s %s" % (opts, action)

    def get_repos(self):
        """Gets the list of enabled repositories."""
        return runcmd(("grep -h ^deb /etc/apt/sources.list "
                       "/etc/apt/sources.list.d/*")).split('\n')

    def remove_repo(self, repolist):
        """Remove all the appearances of a list of repositories.

        :repolist: list of repository names.
        """
        install("software-properties-common")
        available_repos = self.get_repos()

        for repo in repolist:
            for available_repo in available_repos:
                if available_repo.find(repo) != -1:
                    runcmd("apt-add-repository -r '%s'" % available_repo)
                    api.info("Existing repository removed: %s"
                             % available_repo)

    def get_pkglist(self, r):
        d = {}
        for line in r.split('\n'):
            m = re.search(("^Setting up ([a-zA-Z-]+) "
                           "\((.+)\)"), line)
            if m:
                pkg, version = m.groups()
                d[pkg] = '-'.join([pkg, version])
        return d


class PkgTool(object):
    def __init__(self):
        self.client = {
            "centos": Yum,
            "debian": Apt,
            "redhat": Yum,
            "ubuntu": Apt,
        }[system.distname]()
        self.dryrun = False

    def get_path(self):
        return self.client.path

    def get_extension(self):
        return self.client.extension

    def get_repodir(self):
        return self.client.repodir

    def get_pkglist(self, r):
        return self.client.get_pkglist(r)

    def get_repos(self):
        return self.client.get_repos()

    def enable_repo(self, repolist):
        if not os.path.exists(self.client.path):
            os.makedirs(self.client.path)
        l = []
        for repo in to_list(repolist):
            r = runcmd("wget %s -O %s" % (repo,
                                          os.path.join(
                                              self.client.path,
                                              os.path.basename(repo))))
            if r.failed:
                l.append(repo)
        return l

    def remove_repo(self, repolist):
        return self.client.remove_repo(to_list(repolist))

    def install(self, pkgs, enable_repo=[]):
        if enable_repo:
            self.enable_repo(enable_repo)
        return self._exec(action="install", pkgs=pkgs)

    def refresh(self):
        return self._exec(action="refresh")

    def remove(self, pkgs):
        return self._exec(action="remove", pkgs=pkgs)

    def update(self):
        return self._exec(action="update")

    def _exec(self, action, pkgs=None):
        try:
            if pkgs:
                pkgs = to_list(pkgs)
                return self.client.run(action, self.dryrun, pkgs=pkgs)
            else:
                return self.client.run(action, self.dryrun)
        except KeyError:
            raise exception.InstallException("'%s' OS not supported"
                                             % system.distname)


def show_exec_banner():
        """Displays execution banner."""
        cfg = config.CFG.copy()

        print(u'\n\u250C %s ' % colors.green(" UMD verification app")
              + u'\u2500' * 49 + u'\u2510')
        print(u'\u2502' + u' ' * 72 + u'\u2502')
        print(u'\u2502%s %s' % ("Quality criteria:".rjust(25),
              colors.blue("http://egi-qc.github.io"))
              + u' ' * 23 + u'\u2502')
        print(u'\u2502%s %s' % ("Codebase:".rjust(25),
              colors.blue("https://github.com/egi-qc/umd-verification"))
              + u' ' * 4 + u'\u2502')
        print(u'\u2502' + u' ' * 72 + u'\u2502')
        print(u'\u2502' + u' ' * 7 + u'\u2500' * 65 + u'\u2518')

        print(u'\u2502' + u' ' * 72)
        if "repository_url" in cfg.keys() and cfg["repository_url"]:
            print(u'\u2502 Verification repositories used:')
            repos = to_list(cfg.pop("repository_url"))
            for repo in repos:
                print(u'\u2502\t%s' % colors.blue(repo))

        print(u'\u2502')
        print(u'\u2502 Repository basic configuration:')
        basic_repo = ["umd_release", "igtf_repo"]
        if system.distname in ["redhat", "centos"]:
            basic_repo.append("epel_release")
        for k in basic_repo:
            v = cfg.pop(k)
            leftjust = len(max(basic_repo, key=len)) + 5
            print(u'\u2502\t%s %s' % (k.ljust(leftjust), colors.blue(v)))

        print(u'\u2502')
        print(u'\u2502 Path locations:')
        for k in ["log_path", "yaim_path", "puppet_path"]:
            v = cfg.pop(k)
            leftjust = len(max(basic_repo, key=len)) + 5
            print(u'\u2502\t%s %s' % (k.ljust(leftjust), v))

        if cfg["qc_envvars"]:
            print(u'\u2502')
            print(u'\u2502 Local environment variables passed:')
            leftjust = len(max(cfg["qc_envvars"], key=len)) + 5
            for k, v in cfg["qc_envvars"].items():
                cfg.pop("qcenv_%s" % k)
                print(u'\u2502\t%s %s' % (k.ljust(leftjust), v))

        print(u'\u2502')
        print(u'\u2514' + u'\u2500' * 72)


def check_input():
    """Performs a list of checks based on input parameters."""
    # 1) Type of installation
    if config.CFG["installation_type"]:
        api.info("Installation type: %s" % config.CFG["installation_type"])
    else:
        api.fail(("Need to provide the type of installation to be performed: "
                  "(install, upgrade)"), do_abort=True)
    # 2) Verification repository URL
    if not config.CFG["repository_url"]:
        api.warn("No verification repository URL provided.")
    # 3) Metapackage
    if config.CFG["metapkg"]:
        msg = "Metapackage/s selected: %s" % ''.join([
            "\n\t+ %s" % mpkg for mpkg in config.CFG["metapkg"]])
        api.info(msg)
    print(u'\u2500' * 73)


def get_class_attrs(obj):
    """Retuns a list of the class attributes for a given object."""
    return dict([(attr, getattr(obj, attr))
                 for attr in dict(inspect.getmembers(
                     obj,
                     lambda a:not(inspect.isroutine(a)))).keys()
                 if not attr.startswith('__')])


def install(pkgs, enable_repo=[]):
    """Shortcut for package installations."""
    pkgtool = PkgTool()
    return runcmd(pkgtool.install(pkgs, enable_repo))


def get_repos():
    """Shortcut for getting enabled repositories in the system."""
    pkgtool = PkgTool()
    return pkgtool.get_repos()


def remove_repo(repo):
    """Shortcut for removing repository files."""
    pkgtool = PkgTool()
    return pkgtool.remove_repo(repo)


def is_on_path(prog):
    """Checks if a given executable is on the current PATH."""
    r = runcmd("which %s" % prog)
    if r.failed:
        return False
    else:
        return r


def clone_repo(repotype, repourl):
    """Clone a repository in a temporary directory."""
    dirname = tempfile.mkdtemp()

    if repotype in ["git"]:
        if not is_on_path("git"):
            r = install("git")
            if r.failed:
                api.fail("Could not install 'git'.")
        cmd = "git clone %s %s" % (repourl, dirname)
    elif repotype in ["hg", "mercurial"]:
        if not is_on_path("hg"):
            r = install("mercurial")
            if r.failed:
                api.fail("Could not install 'mercurial'.")
        cmd = "hg clone %s %s" % (repourl, dirname)
    else:
        raise NotImplementedError(("Current implementation does not support "
                                   "repository type '%s'" % repotype))

    r = runcmd(cmd)
    if r.failed:
        api.fail("Could not clone repository '%s' (via %s)"
                 % (repourl, repotype))
        dirname = None
        os.rmdir(dirname)
    return dirname

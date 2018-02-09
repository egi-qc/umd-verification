import contextlib
import inspect
import os
import os.path
import re
import shutil
import tempfile

import fabric
from fabric import api as fabric_api
from fabric import colors
import jinja2
import mock
import yaml

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
        fname = os.path.join(config.CFG["log_path"], fname)
        _write_type = 'w'
        if os.path.isfile(fname):
           _write_type = 'a'
        with open(fname, _write_type) as f:
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


def create_workspace():
    """Create workspace (logs, ..) removing any previous existence."""
    if os.path.exists(config.CFG["log_path"]):
        shutil.rmtree(config.CFG["log_path"])
    os.makedirs(config.CFG["log_path"])
    api.info("Log directory '%s' has been created." % config.CFG["log_path"])


def filelog(f):
    """Decorator method to write command's output to file."""
    def _log(*args, **kwargs):
        logfile = kwargs.pop("log_to_file", None)
        stop_on_error = kwargs.pop("stop_on_error", True)
        r = f(*args, **kwargs)
        if logfile:
            r.logfile = to_file(r, logfile)
        if r.failed:
            msg = ("Command execution has failed (reason: \"%s\")"
                   % r.stderr.replace('\n', ' '))
            if not stop_on_error:
                msg += " (action: no exit)"
            if logfile:
                msg += " (log: %s)" % r.logfile
            api.fail(msg, stop_on_error=stop_on_error)
        return r
    return _log


@filelog
def runcmd(cmd,
           stderr_to_stdout=False,
           nosudo=False,
           envvars=[]):
    """Runs a generic command.

    :cmd: command to execute
    """
    if stderr_to_stdout:
        cmd = ' '.join([cmd, "2>&1"])
    qc_envvars = config.CFG.get("qc_envvars", {})
    env_d = dict(qc_envvars.items()
                 + [("LC_ALL", "en_US.UTF-8"), ("LANG", "en_US.UTF-8")]
                 + envvars)

    with contextlib.nested(fabric_api.settings(warn_only=True),
                           fabric_api.shell_env(**env_d)):
        if not nosudo:
            cmd = "sudo -E " + cmd
        else:
            if system.distro_version == "redhat6":
                cmd = "/usr/local/rvm/bin/rvmsudo " + cmd
            else:
                cmd = "sudo su %s -c '%s'" % (nosudo, cmd)

        r = fabric_api.local(cmd, capture=True)
    return r


@filelog
def runcmd_chdir(cmd,
                 chdir,
                 stderr_to_stdout=False,
                 nosudo=False,
                 envvars=[]):
    """Runs a generic command based on a given directory

    :cmd: command to execute
    :chdir: directory to execute the command from
    """
    if stderr_to_stdout:
        cmd = ' '.join([cmd, "2>&1"])
    qc_envvars = config.CFG.get("qc_envvars", {})
    env_d = dict(qc_envvars.items()
                 + [("LC_ALL", "en_US.UTF-8"), ("LANG", "en_US.UTF-8")]
                 + envvars)
    with contextlib.nested(fabric.context_managers.lcd(chdir),
                           fabric_api.settings(warn_only=True),
                           fabric_api.shell_env(**env_d)):
        if not nosudo:
            cmd = "sudo -E " + cmd
        r = fabric_api.local(cmd, capture=True)
    return r


class Yum(object):
    def __init__(self):
        self.path = "/etc/yum.repos.d/"
        self.config = "/etc/yum.conf"
        self.extension = ".repo"
        self.pkg_extension = ".rpm"

    def _validate_output(self, r):
        """Checks the validity of the yum output message."""
        has_failed = False
        for line in r.split('\n'):
            m = re.search("(.+): does not update installed package.", line)
            if m:
                has_failed = False

            m = re.search("Package (matching ){0,1}(.+) already installed",
                          line)
        if has_failed:
            r.failed = True
        else:
            r.failed = False
        return r

    def run(self, action, dryrun, pkgs=None):
        if action == "install-remote":
            for _pkg in pkgs:
                r = runcmd("rpm -ivh %s" % _pkg)
            return r
        else:
            opts = ''
            if dryrun:
                if system.distro_version == "redhat5":
                    runcmd("yum -y install yum-downloadonly")
                elif system.distro_version == "redhat6":
                    runcmd("yum -y install yum-plugin-downloadonly")
                opts = "--downloadonly"

            if action == "refresh":
                runcmd("yum clean all")
                action = "makecache fast"

            if pkgs:
                r = runcmd("yum -y %s %s %s" % (opts, action, " ".join(pkgs)))
            else:
                r = runcmd("yum -y %s %s" % (opts, action))

            return self._validate_output(r)

    def get_pkglist(self, r):
        """Gets the list of packages being installed parsing yum output."""
        d = {}
        lines = r.split('\n')
        try:
            for line in lines[lines.index("Installed:"):]:
                if line.startswith(' '):
                    for pkg in map(None, *([iter(line.split())] * 2)):
                        name, version = pkg
                        name, arch = name.rsplit('.', 1)
                        version = version.split(':')[-1]
                        d[name] = '.'.join(['-'.join([name, version]), arch])
        except ValueError:
            api.info("No new package installed.")

        # Look for already installed packages
        for line in r.split('\n'):
            m = re.search(("Package (matching ){0,1}(.+) already "
                           "installed"), line)
            if m:
                all = m.groups()[-1]
                pattern = "([a-zA-Z0-9-_]+)-\d+.+"
                name = re.search(pattern, all).groups()[0]
                d[name] = ' '.join([all, "(already installed)"])

        return d

    def get_repo_from_pkg(self, pkglist):
        d = {}
        r = runcmd("yum -q list %s" % ' '.join(pkglist),
                   stop_on_error=False)
        if not r.failed:
            for line in r.split('\n'):
                fields = line.split()
                if len(fields) == 3:
                    pkg, version, repository = fields
                    pkg = pkg.split('.')[0]
                    d[pkg] = repository
        else:
            api.fail("Could not get package's repository information")
        return d

    def get_repos(self):
        l = []
        is_repo = False
        for line in runcmd("yum repolist",
                           stop_on_error=False).split('\n'):
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
            r = runcmd("grep %s %s/* | cut -d':' -f1|uniq" % (repo, self.path),
                       stop_on_error=False)
            if r:
                for f in r.split('\n'):
                    os.remove(f)
                    api.info("Existing repository '%s' removed." % f)

    def disable_repo(self, repo):
        """Sets repositories as disabled.

        :repo: repository name
        """
        r = runcmd("grep %s %s/* | cut -d':' -f1|uniq" % (repo, self.path),
                   stop_on_error=False)
        if r:
            f = r.split('\n')[0]
            r_disable = runcmd(("sed -i 's/enabled.*=.*1/enabled=0/g' "
                                "%s" % f),
                               stop_on_error=False)
            r = r_disable
        return r

    def add_repo_key(self, keylist):
        for key in keylist:
            r = runcmd("rpm --import %s" % key,
                       stop_on_error=False)
            if r.failed:
                api.fail("Could not add key '%s'" % key)
            else:
                api.info("Repository key added: %s" % key)

    def add_repo(self, repo, **kwargs):
        if "name" in kwargs.keys():
            name = kwargs["name"]
            if "local_repo" in kwargs.keys():
                r = runcmd("yum-config-manager --enable %s" % name)
            else:
                priority = kwargs["priority"]
                lrepo = ["[%s]" % name.replace(' ', '_'),
                         "name=%s" % name,
                         "baseurl=%s" % repo,
                         "priority=%s" % priority,
                         "protect=1",
                         "enabled=1",
                         "gpgcheck=0"]
                if "priority" in kwargs.keys():
                    lrepo.append("priority=%s" % kwargs["priority"])
                fname = os.path.join(self.path,
                                     name.replace(' ', '') + self.extension)
                with open(fname, 'w') as f:
                    for line in lrepo:
                        f.write(line + '\n')
                r = mock.MagicMock()
                r.failed = False
        else:
            r = runcmd("wget %s -O %s" % (repo,
                                          os.path.join(
                                              self.path,
                                              os.path.basename(repo))),
                       stop_on_error=False)
        return r

    def handle_repo_ssl(self):
        """Removes SSL verification for https repositories."""
        r = runcmd("sed -i 's/^sslverify.*/sslverify=False/g' %s"
                   % self.config,
                   stop_on_error=False)
        if r.failed:
            api.fail("Could not disable SSL in %s" % self.config)

    def get_pkg_version(self, rpmfile, check_installed=True):
        """Extracts name&version from RPM file. Returns a (name, version) dict

        :rpmfile: absolute path poiting to a RPM file
        :check_installed: True if the package is already installed
        """
        d = {}
        opts = "-q"
        if not check_installed:
            opts = "-qp"
        r = runcmd(("rpm %s --queryformat '%%{NAME} %%{VERSION}-%%{RELEASE}"
                    ".%%{ARCH}\\n' %s" % (opts, rpmfile)),
                   stop_on_error=False)
        if not r.failed:
            for pkg in r.split('\n'):
                name, version = pkg.split()
                if name in d.keys():
                    try:
                        d[name].append(version)
                    except AttributeError:
                        l = [d[name], version]
                        d[name] = l
                else:
                    d[name] = version

        return d

    def join_pkg_version(self, pkgs):
        return ['-'.join(list(pkg)) for pkg in pkgs if isinstance(pkg, tuple)]

    def is_pkg_installed(self, pkg):
        return not runcmd("rpm --quiet -q %s" % pkg,
                          stop_on_error=False).failed


class Apt(object):
    def __init__(self):
        self.path = "/etc/apt/sources.list.d/"
        self.extension = ".list"
        self.pkg_extension = ".deb"

    def run(self, action, dryrun, pkgs=None):
        def _download_pkg(l):
            _l = []
            for _pkg in l:
                _dest = os.path.join("/tmp", os.path.basename(_pkg))
                runcmd("wget %s -O %s" % (_pkg, _dest))
                if os.path.exists(_dest):
                    _l.append(_dest)
            return _l

        cmd = None
        opts = ''

        if dryrun:
            opts = "--dry-run"

        if action == "refresh":
            action = "update"
        elif action == "install-remote":
            action = "install"
            pkgs = _download_pkg(pkgs)

        if pkgs:
            if os.path.exists(pkgs[0]):
                cmd = "dpkg -i %s" % " ".join(pkgs)
            else:
                cmd = "apt-get -y %s %s %s" % (opts,
                                               action,
                                               " ".join(pkgs))
        else:
            cmd = "apt-get -y %s %s" % (opts, action)

        return runcmd(cmd,
                      envvars=[("DEBIAN_FRONTEND", "noninteractive")],
                      stop_on_error=False)

    def get_repos(self):
        """Gets the list of enabled repositories."""
        return runcmd(("grep -h ^deb /etc/apt/sources.list "
                       "/etc/apt/sources.list.d/*"),
                      stop_on_error=False).split('\n')

    def get_repo_from_pkg(self, pkglist):
        # NOTE(orviz) There is no easy way to know from which repository
        # a package was installed
        return {}

    def remove_repo(self, repolist):
        """Remove all the appearances of a list of repositories.

        :repolist: list of repository names.
        """
        self.run("install", False, pkgs=["software-properties-common"])
        available_repos = self.get_repos()

        for repo in repolist:
            for available_repo in available_repos:
                if available_repo.find(repo) != -1:
                    runcmd("apt-add-repository -y -r '%s'" % available_repo,
                           stop_on_error=False)
                    api.info("Existing repository removed: %s"
                             % available_repo)

    def add_repo_key(self, keylist):
        for key in keylist:
            runcmd("wget -q %s -O /tmp/key.key" % key,
                   stop_on_error=False)
            r = runcmd("apt-key add /tmp/key.key",
                       stop_on_error=False)
            if r.failed:
                api.fail("Could not add key '%s'" % key)
            else:
                api.info("Repository key added: %s" % key)

    def add_repo(self, repo, **kwargs):
        """Adds a Debian repository URL.

        :repo: Debian formatted repo URL. If not, tries to get it by parsing
               the URL (note that only one component will be added).
        """
        # Parse URL in not Debian-formatted or PPA
        if len(repo.split(' ')) == 1 and not re.search(":(?!//)", repo):
            uri, rest = repo.split("dists")
            rest = rest.strip('/').split('/')
            rest.pop(0)  # distro
            if not rest:
                # 'main' as the default component
                component = ["main"]
            else:
                component = rest.pop(0)
            repo = ' '.join([uri, component])

        self.run("install", False, pkgs=["software-properties-common"])
        return runcmd("apt-add-repository -y '%s'" % repo,
                      stop_on_error=False)

    def get_pkglist(self, r):
        d = {}
        for line in r.split('\n'):
            for p in ["^Setting up ([a-zA-Z-]+) \((.+)\)",
                      "([a-zA-Z0-9-]+) is already the newest version"]:
                m = re.search(p, line)
                if m:
                    try:
                        pkg, version = m.groups()
                    except ValueError:  # no version available
                        pkg = m.groups()[0]
                        version = self.get_pkg_version(pkg)[pkg]
                    d[pkg] = '-'.join([pkg, version])
                    break
        return d

    def get_pkg_version(self, debfile, check_installed=True):
        d = {}

        if check_installed:
            cmd = "dpkg-query"
        else:
            cmd = "dpkg-deb"
        r = runcmd("%s -W %s" % (cmd, debfile),
                   stop_on_error=False)
        if not r.failed:
            name, version = r.split()
            d[name] = version
        return d

    def join_pkg_version(self, pkgs):
        return ['='.join(list(pkg)) for pkg in pkgs if isinstance(pkg, tuple)]

    def is_pkg_installed(self, pkg):
        return not runcmd("dpkg -l %s" % pkg, stop_on_error=False).failed

    def handle_repo_ssl(self):
        raise NotImplementedError

    def disable_repo(self):
        raise NotImplementedError


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

    def get_pkg_extension(self):
        return self.client.pkg_extension

    def get_pkglist(self, r):
        return self.client.get_pkglist(r)

    def get_repo_from_pkg(self, pkglist):
        """Returns the repository from where the package was installed."""
        return self.client.get_repo_from_pkg(to_list(pkglist))

    def get_repos(self):
        return self.client.get_repos()

    def add_repo_key(self, key):
        return self.client.add_repo_key(to_list(key))

    def enable_repo(self, repolist, **kwargs):
        if not os.path.exists(self.client.path):
            os.makedirs(self.client.path)
        for repo in to_list(repolist):
            r = self.client.add_repo(repo, **kwargs)
            if r.failed:
                api.fail("Could not add repo '%s'" % repo)
            else:
                api.info("Repository '%s' added" % repo)

    def disable_repo(self, repolist):
        for repo in to_list(repolist):
            r = self.client.disable_repo(repo)
            if r.failed:
                api.fail("Could not disable repo '%s'" % repo)
            else:
                api.info("Repository '%s' disabled" % repo)

    def remove_repo(self, repolist):
        return self.client.remove_repo(to_list(repolist))

    def handle_repo_ssl(self):
        return self.client.handle_repo_ssl()

    @filelog
    def install(self, pkgs, enable_repo=[], key_repo=[]):
        if enable_repo:
            self.enable_repo(enable_repo)
            if key_repo:
                self.add_repo_key(to_list(key_repo))
            self.refresh()
        return self._exec(action="install", pkgs=pkgs)

    @filelog
    def install_remote(self, pkgs, enable_repo=[], key_repo=[]):
        if enable_repo:
            self.enable_repo(enable_repo)
            if key_repo:
                self.add_repo_key(to_list(key_repo))
            self.refresh()
        return self._exec(action="install-remote", pkgs=pkgs)

    @filelog
    def refresh(self):
        return self._exec(action="refresh")

    @filelog
    def remove(self, pkgs):
        return self._exec(action="remove", pkgs=pkgs)

    @filelog
    def update(self):
        return self._exec(action="update")

    def _exec(self, action, pkgs=None):
        try:
            if pkgs:
                pkgs = to_list(pkgs)
                r = self.client.run(action, self.dryrun, pkgs=pkgs)
            else:
                r = self.client.run(action, self.dryrun)
            return r
        except KeyError:
            raise exception.InstallException("'%s' OS not supported"
                                             % system.distname)

    def get_pkg_version(self, pkgfile, check_installed=True):
        return self.client.get_pkg_version(pkgfile, check_installed)

    def join_pkg_version(self, pkgs):
        """Returns a list of strings with the 'pkg:version' format name."""
        pkgs = to_list(pkgs)
        return self.client.join_pkg_version(pkgs)

    def is_pkg_installed(self, pkg):
        """Checks if the package (name) is installed."""
        return self.client.is_pkg_installed(pkg)


def show_exec_banner_ascii():
    """Displays execution banner (ascii)."""
    cfg = config.CFG.copy()

    basic_repo = ["umd_release_pkg", "igtf_repo"]

    print(u'\n')
    print(colors.green(u'UMD verification tool').center(120))
    print(u'=====================\n'.center(111))
    print((u'%s: %s' % (colors.white(u'Quality criteria'),
                        colors.blue(u'http://egi-qc.github.io'))).center(120))
    print((u'%s: %s' % (
        colors.white(u'Codebase'),
        colors.blue(("https://github.com/egi-qc/"
                     "umd-verification")))).center(120))
    print(u'')
    print(u'\t%s' % colors.white(u'Path locations'))
    print(u'\t %s' % colors.white('|'))
    for k in ["log_path", "yaim_path", "puppet_path"]:
        v = cfg.pop(k)
        leftjust = len(max(basic_repo, key=len)) + 5
        print(u'\t %s %s %s' % (colors.white('|'), k.ljust(leftjust), v))
    print(u'\t')
    print(u'\t%s' % colors.white(u'Production repositories'))
    print(u'\t %s' % colors.white('|'))
    for repo in basic_repo:
        try:
            v = cfg.pop(repo)
        except KeyError:
            v = None
        leftjust = len(max(basic_repo, key=len)) + 5
        print(u'\t %s %s %s' % (colors.white('|'),
                                repo.ljust(leftjust),
                                colors.blue(v)))
    print(u'\n\n')

    if "repository_url" in cfg.keys():
        api.info("Using the following UMD verification repositories")
        repos = to_list(cfg.pop("repository_url"))
        for repo in repos:
            print(u'\t+ %s' % colors.blue(repo))

    if "repository_file" in cfg.keys():
        api.info("Using the following repository files")
        repos = to_list(cfg.pop("repository_file"))
        for repo in repos:
            print(u'\t+ %s' % colors.blue(repo))


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

    if "repository_file" in cfg.keys():
        print(u'\u2502 Verification repositories (files) used:')
        repos = to_list(cfg.pop("repository_file"))
        for repo in repos:
            print(u'\u2502\t%s' % colors.blue(repo))

    print(u'\u2502')
    print(u'\u2502 Repository basic configuration:')
    basic_repo = ["umd_release", "igtf_repo"]
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


def get_class_attrs(obj):
    """Retuns a list of the class attributes for a given object."""
    return dict([(attr, getattr(obj, attr))
                 for attr in dict(inspect.getmembers(
                     obj,
                     lambda a:not(inspect.isroutine(a)))).keys()
                 if not attr.startswith('__')])


@filelog
def install(pkgs, enable_repo=[], key_repo=[]):
    """Shortcut for package installations."""
    pkgtool = PkgTool()
    return pkgtool.install(pkgs, enable_repo, key_repo)


@filelog
def install_remote(pkgs, enable_repo=[], key_repo=[]):
    """Shortcut for remote package installations."""
    pkgtool = PkgTool()
    return pkgtool.install_remote(pkgs, enable_repo, key_repo)


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


def enable_repo(repo, **kwargs):
    pkgtool = PkgTool()
    return pkgtool.enable_repo(repo, **kwargs)


def add_repo_key(keyurl):
    pkgtool = PkgTool()
    return pkgtool.add_repo_key(keyurl)


def join_pkg_version(pkg):
    pkgtool = PkgTool()
    return pkgtool.join_pkg_version(pkg)


def is_pkg_installed(pkg):
    pkgtool = PkgTool()
    return pkgtool.is_pkg_installed(pkg)


def load_from_hiera(fname):
    """Returns a dictionary with the content of fname.

    :fname: YAML filename to load (could be a list).
    """
    d = {}
    for f in to_list(fname):
        d.update(yaml.load(file("etc/puppet/%s" % f, "r")))
    return d


def hiera(v):
    """Find variable value through hiera."""
    return runcmd("hiera -c /etc/puppet/hiera.yaml '%s'" % v)


def find_extension_files(path, extension):
    """Finds all ocurrences of a given file extension.

    :path: Path where to look for
    :extension: file extension
    """
    l = []
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith(extension):
                l.append(os.path.join(root, f))
    return l


def to_yaml(fname, lines, destroy=False):
    """Creates a YAML file with the content given (string)."""
    lines = to_list(lines)
    write_type = 'a'
    if destroy:
        write_type = 'w'
    with open(fname, write_type) as f:
        for line in lines:
            f.write(yaml.safe_dump(yaml.safe_load(line), default_flow_style=False))
    return fname


def render_jinja(template, data, output_file=None):
    """Stores in a file the output of rendering a Jinja2 template.

    :template: template file name (neither absolute nor relative path)
    :data: data to be rendered in the template
    :output_file: absolute path to the file to put the rendered result
    """
    template_file = os.path.join(
        os.getcwd(),
        os.path.join(config.CFG["jinja_template_dir"],
                     template))
    templateLoader = jinja2.FileSystemLoader('/')
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(template_file)
    out = template.render(data)
    with open(output_file, 'w') as f:
        f.write(out)
        f.flush()
    return output_file

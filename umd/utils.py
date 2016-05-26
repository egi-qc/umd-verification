import inspect
import os
import os.path
import re
import shutil
import tempfile

from fabric import api as fabric_api
from fabric import colors
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
        dirname = os.path.dirname(fname)
        if not dirname:
            dirname = config.CFG["log_path"]
        if not os.path.exists(dirname):
            os.makedirs(dirname)
            api.info("Log directory '%s' has been created." % dirname)
        fname = os.path.join(dirname, fname)
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


def filelog(f):
    """Decorator method to write command's output to file."""
    def _log(*args, **kwargs):
        logfile = kwargs.pop("log_to_file", None)
        r = f(*args, **kwargs)
        if logfile:
            r.logfile = to_file(r, logfile)
        return r
    return _log


@filelog
def runcmd(cmd, stderr_to_stdout=False):
    """Runs a generic command.

    :cmd: command to execute
    """
    if stderr_to_stdout:
        cmd = ' '.join([cmd, "2>&1"])
    qc_envvars = config.CFG.get("qc_envvars", {})
    env_d = dict(qc_envvars.items()
                 + [("LC_ALL", "en_US.UTF-8"), ("LANG", "en_US.UTF-8")])
    with fabric_api.settings(warn_only=True):
        with fabric_api.shell_env(**env_d):
            # FIXME(orviz) use sudo fabric function
            r = fabric_api.local("sudo -E " + cmd, capture=True)
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
        r = runcmd("yum -q list %s" % ' '.join(pkglist))
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

    def add_repo_key(self, keylist):
        for key in keylist:
            r = runcmd("rpm --import %s" % key)

            if r.failed:
                api.fail("Could not add key '%s'" % key)
            else:
                api.info("Repository key added: %s" % key)

    def add_repo(self, repo, **kwargs):
        if "name" in kwargs.keys():
            name = kwargs["name"]
            lrepo = ["[%s]" % name.replace(' ', '_'),
                     "name=%s" % name,
                     "baseurl=%s" % repo,
                     "protect=1",
                     "enabled=1",
                     "priority=%s" % kwargs["priority"],
                     "gpgcheck=0"]
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
                                              os.path.basename(repo))))
        return r

    def handle_repo_ssl(self):
        """Removes SSL verification for https repositories."""
        r = runcmd("sed -i 's/^sslverify.*/sslverify=False/g' %s"
                   % self.config)
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
                    ".%%{ARCH}\\n' %s" % (opts, rpmfile)))
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


class Apt(object):
    def __init__(self):
        self.path = "/etc/apt/sources.list.d/"
        self.extension = ".list"
        self.pkg_extension = ".deb"

    def run(self, action, dryrun, pkgs=None):
        cmd = None
        opts = ''

        if dryrun:
            opts = "--dry-run"

        if action == "refresh":
            action = "update"

        if pkgs:
            if os.path.exists(pkgs[0]):
                cmd = "dpkg -i %s" % " ".join(pkgs)
            else:
                cmd = "apt-get -y %s %s %s" % (opts,
                                               action,
                                               " ".join(pkgs))
        else:
            cmd = "apt-get -y %s %s" % (opts, action)

        return runcmd(cmd)

    def get_repos(self):
        """Gets the list of enabled repositories."""
        return runcmd(("grep -h ^deb /etc/apt/sources.list "
                       "/etc/apt/sources.list.d/*")).split('\n')

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
                    runcmd("apt-add-repository -y -r '%s'" % available_repo)
                    api.info("Existing repository removed: %s"
                             % available_repo)

    def add_repo_key(self, keylist):
        for key in keylist:
            runcmd("wget -q %s -O /tmp/key.key" % key)
            r = runcmd("apt-key add /tmp/key.key")
            if r.failed:
                api.fail("Could not add key '%s'" % key)
            else:
                api.info("Repository key added: %s" % key)

    def add_repo(self, repo):
        self.run("install", False, pkgs=["software-properties-common"])
        return runcmd("apt-add-repository -y '%s'" % repo)

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
        r = runcmd("%s -W %s" % (cmd, debfile))
        if not r.failed:
            name, version = r.split()
            d[name] = version
        return d

    def join_pkg_version(self, pkgs):
        return ['='.join(list(pkg)) for pkg in pkgs if isinstance(pkg, tuple)]

    def handle_repo_ssl(self):
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


def show_exec_banner_ascii():
    """Displays execution banner (ascii)."""
    cfg = config.CFG.copy()

    basic_repo = ["umd_release_pkg", "igtf_repo"]
    if system.distname in ["redhat", "centos"]:
        basic_repo.append("epel_release")

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
        v = cfg.pop(repo)
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


def load_from_hiera(fname):
    """Returns a dictionary with the content of fname.

    :fname: YAML filename to load.
    """
    return yaml.load(file("etc/puppet/%s" % fname, "r"))


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


def remove_logs():
    """Creates a new execution log directory."""
    if os.path.exists(config.CFG["log_path"]):
        shutil.rmtree(config.CFG["log_path"])

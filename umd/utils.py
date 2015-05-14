import os.path

from fabric.api import abort
from fabric.api import local
from fabric.api import settings
from fabric.colors import blue
from fabric.colors import green
from fabric.colors import red
from fabric.context_managers import lcd

from umd import exception
from umd import system
from umd.api import info
from umd.api import fail


def to_list(obj):
    if not isinstance(obj, (str, list)):
        raise exception.ConfigException("obj variable type '%s' not supported."
                                        % type(obj))
    elif isinstance(obj, str):
        return [obj]
    return obj


def to_file(r, logfile):
    """Writes Fabric capture result to the given file."""
    def _write(fname, msg):
        dirname = os.path.dirname(fname)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
            info("Log directory '%s' has been created.")
        with open(fname, 'a') as f:
            f.write(msg)
            f.flush()

    l = []
    if r.stdout:
        _fname = '.'.join([logfile, "stdout"])
        _write(_fname, r.stdout)
        l.append(_fname)
    if r.stderr:
        _fname = '.'.join([logfile, "stderr"])
        _write(_fname, r.stderr)
        l.append(_fname)

    return l


def format_error_msg(logs, cmd=None):
    msg = "See more information in logs (%s)." % ','.join(logs)
    if cmd:
        msg = ' '.join(["Error while executing command '%s'.", msg])
    return msg


def runcmd(cmd, chdir=None, fail_check=True, logfile=None, stderr_to_stdout=False):
    """Runs a generic command.
            cmd: command to execute.
            chdir: local directory to run the command from.
            fail_check: boolean that indicates if the workflow must be
                interrupted in case of failure.
            logfile: file to log the command execution.
    """
    if stderr_to_stdout:
        cmd = ' '.join([cmd, "2>&1"])

    if chdir:
        with lcd(chdir):
            with settings(warn_only=True):
                r = local(cmd, capture=True)
    else:
        with settings(warn_only=True):
            r = local(cmd, capture=True)

    logs = []
    if logfile:
        logs = to_file(r, logfile)

    if r.failed:
        msg = format_error_msg(logs, cmd)
        if fail_check:
            abort(fail(msg % cmd))
        else:
            fail(msg % cmd)

    if logs:
        return r, logs
    return r


def yum(action, pkgs=None):
    if pkgs:
        return "yum -y %s %s" % (action, " ".join(pkgs))
    else:
        return "yum -y %s" % action


class PkgTool(object):
    PKGTOOL = {
        "redhat": yum,
    }
    REPOPATH = {
        "redhat": "/etc/yum.repos.d/",
    }

    def _enable_repo(self, repofile):
        runcmd("wget %s -O %s" % (repofile,
                                  os.path.join(self.REPOPATH[system.distname],
                                               os.path.basename(repofile))))

    def get_path(self):
        return self.REPOPATH[system.distname]

    def install(self, pkgs, repofile=None):
        if repofile:
            self._enable_repo(repofile)
        return self._exec(action="install", pkgs=pkgs)

    def remove(self, pkgs):
        return self._exec(action="remove", pkgs=pkgs)

    def update(self):
        return self._exec(action="update")

    def _exec(self, action, pkgs=None):
        try:
            if pkgs:
                pkgs = to_list(pkgs)
                return self.PKGTOOL[system.distname](action, pkgs)
            else:
                return self.PKGTOOL[system.distname](action)
        except KeyError:
            raise exception.InstallException("'%s' OS not supported"
                                             % system.distname)


def install(pkgs, repofile=None):
    """Shortcut for package installations."""
    pkgtool = PkgTool()
    return runcmd(pkgtool.install(pkgs, repofile))


def show_exec_banner(cfgdict, qc_envvars):
        """Displays execution banner."""
        cfg = cfgdict.copy()

        print(u'\n\u250C %s ' % green(" UMD verification app") + u'\u2500'*49 + u'\u2510')
        print(u'\u2502' + u' '*72 + u'\u2502')
        print(u'\u2502%s %s' % ("Quality criteria:".rjust(25), blue("http://egi-qc.github.io"))+ u' '*23 + u'\u2502')
        print(u'\u2502%s %s' % ("Codebase:".rjust(25), blue("https://github.com/egi-qc/umd-verification")) + u' '*4 + u'\u2502')
        print(u'\u2502' + u' '*72 + u'\u2502')
        print(u'\u2502' + u' '*7+ u'\u2500'*65 + u'\u2518')

        print(u'\u2502' + u' '*72)
        if "repository_url" in cfg.keys():
            print(u'\u2502 Verification repositories used:')
            repos = to_list(cfg.pop("repository_url"))
            for repo in repos:
                print(u'\u2502\t%s' % blue(repo))

        print(u'\u2502')
        print(u'\u2502 Repository basic configuration:')
        basic_repo = ["epel_release", "umd_release", "igtf_repo"]
        for k in basic_repo:
            v = cfg.pop(k)
            leftjust = len(max(basic_repo, key=len))+5
            print(u'\u2502\t%s %s' % (k.ljust(leftjust), blue(v)))

        print(u'\u2502')
        print(u'\u2502 Path locations:')
        for k in ["log_path", "yaim_path"]:
            v = cfg.pop(k)
            leftjust = len(max(basic_repo, key=len))+5
            print(u'\u2502\t%s %s' % (k.ljust(leftjust), v))

        if qc_envvars:
            print(u'\u2502')
            print(u'\u2502 Local environment variables passed:')
            leftjust = len(max(qc_envvars, key=len))+5
            for k, v in qc_envvars.items():
                cfg.pop("qcenv_%s" % k)
                print(u'\u2502\t%s %s' % (k.ljust(leftjust), v))

        print(u'\u2502')
        print(u'\u2514' + u'\u2500'*72)

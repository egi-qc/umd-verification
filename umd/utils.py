import os.path

from fabric.api import abort
from fabric.api import local
from fabric.api import settings
from fabric.colors import red
from fabric.context_managers import lcd

from umd import exception
from umd import system
from umd.api import info


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
    if isinstance(r, str):  # exception
        _fname = '.'.join([logfile, "stdout"])
        _write(_fname, r)
        l.append(_fname)
    else:
        if r.stdout:
            _fname = '.'.join([logfile, "stdout"])
            _write(_fname, r.stdout)
            l.append(_fname)
        if r.stderr:
            _fname = '.'.join([logfile, "stderr"])
            _write(_fname, r.stderr)
            l.append(_fname)

    return l


def runcmd(cmd, chdir=None, fail_check=True, logfile=None):
    """Runs a generic command.
            cmd: command to execute.
            chdir: local directory to run the command from.
            fail_check: boolean that indicates if the workflow must be
                interrupted in case of failure.
            logfile: file to log the command execution.
    """
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

    if fail_check:
        if r.failed:
            msg = "Error while executing command '%s'."
            if logs:
                msg = ' '.join([msg, "See more information in logs (%s)."
                                     % ','.join(logs)])
            abort(red(msg % cmd))
            # raise exception.ExecuteCommandException(("Error found while "
            #                                          "executing command: "
            #                                          "'%s' (Reason: %s)"
            #                                          % (cmd, r.stderr)))
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

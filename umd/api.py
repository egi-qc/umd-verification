import os

from fabric.api import abort
from fabric.api import local
from fabric.api import puts
from fabric.api import settings
from fabric.colors import red
from fabric.context_managers import lcd

from umd.base.install import utils as inst_utils


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


def info(msg):
    """Prints info/debug logs."""
    puts("[INFO] %s" % msg)


def fail(msg):
    """Prints info/debug logs."""
    abort("[%s] %s" % (red("FAIL"), msg))


def ok(msg):
    """Prints info/debug logs."""
    puts("[OK] %s" % msg)


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

def install(pkgs):
    """Shortcut for package installations."""
    pkgtool = inst_utils.PkgTool()
    return runcmd(pkgtool.install(pkgs))

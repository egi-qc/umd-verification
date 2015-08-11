import sys

from fabric import api as fabric_api
from fabric import colors


def info(msg):
    """Prints info/debug logs."""
    fabric_api.puts("[INFO] %s" % msg)


def fail(msg, do_abort=False):
    """Prints info/debug logs."""
    fabric_api.puts("[%s] %s" % (colors.red("FAIL"), msg))
    if do_abort:
        sys.exit(1)


def ok(msg):
    """Prints info/debug logs."""
    fabric_api.puts("[OK] %s" % msg)


def warn(msg):
    """Prints warn logs."""
    fabric_api.puts("[%s] %s" % (colors.yellow("WARN"), msg))

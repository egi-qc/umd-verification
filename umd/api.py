from fabric.api import abort
from fabric.api import puts
from fabric.colors import red


def info(msg):
    """Prints info/debug logs."""
    puts("[INFO] %s" % msg)


def fail(msg):
    """Prints info/debug logs."""
    abort("[%s] %s" % (red("FAIL"), msg))


def ok(msg):
    """Prints info/debug logs."""
    puts("[OK] %s" % msg)

from fabric import state

from umd.products.argus import *    # NOQA
from umd.products.bdii import *     # NOQA
from umd.products.ca import *       # NOQA
from umd.products.creamce import *  # NOQA
from umd.products.fts import *      # NOQA
from umd.products.glexec import *   # NOQA
from umd.products.globus import *   # NOQA
from umd.products.gram5 import *    # NOQA
from umd.products.myproxy import *  # NOQA
from umd.products.rc import *       # NOQA
from umd.products.storm import *    # NOQA
from umd.products.ui import *       # NOQA


state.output.status = False
state.output.stdout = False
state.output.warnings = False
state.output.running = True
state.output.user = True
state.output.stderr = False
state.output.aborts = False
state.output.debug = False

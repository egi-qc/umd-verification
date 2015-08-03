from fabric.state import output

from umd.products.argus import *
from umd.products.bdii import *
from umd.products.ca import *
from umd.products.creamce import *
from umd.products.glexec import *
from umd.products.myproxy import *
from umd.products.rc import *
from umd.products.storm import *
from umd.products.ui import *


output.status = False
output.stdout = False
output.warnings = False
output.running = True
output.user = True
output.stderr = False
output.aborts = False
output.debug = False

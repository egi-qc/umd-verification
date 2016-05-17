from fabric import state

from umd.products.arc import arc_ce                         # NOQA
from umd.products.argus import argus, argus_yaim, ees       # NOQA
from umd.products.argus import argus_no_metapkg             # NOQA
from umd.products.argus import argus_yaim                   # NOQA
from umd.products.argus import ees                          # NOQA
from umd.products.bdii import bdii_site_puppet              # NOQA
from umd.products.bdii import bdii_site_yaim                # NOQA
from umd.products.bdii import bdii_top_puppet               # NOQA
from umd.products.ca import ca, crl                         # NOQA
from umd.products.canl import canl                          # NOQA
from umd.products.cream import gridenginerized              # NOQA
from umd.products.cream import standalone                   # NOQA
from umd.products.dcache import dcache                      # NOQA
from umd.products.dpm import dpm_1_8_10                     # NOQA
from umd.products.frontier_squid import frontier_squid      # NOQA
from umd.products.fts import fts                            # NOQA
from umd.products.glexec import glexec_wn                   # NOQA
from umd.products.globus import default_security            # NOQA
from umd.products.globus import gridftp                     # NOQA
from umd.products.gram5 import gram5                        # NOQA
from umd.products.gridsite import gridsite                  # NOQA
from umd.products.keystone_voms import keystone_voms_juno   # NOQA
from umd.products.keystone_voms import keystone_voms_kilo   # NOQA
from umd.products.myproxy import myproxy                    # NOQA
from umd.products.rc import rc                              # NOQA
from umd.products.storm import storm                        # NOQA
from umd.products.ui import ui, ui_myproxy, ui_gfal         # NOQA
from umd.products.voms import voms_server                   # NOQA
from umd.products.wms import wms_utils                      # NOQA
from umd.products.xrootd import xrootd                      # NOQA


state.output.status = False
state.output.stdout = False
state.output.warnings = False
state.output.running = True
state.output.user = True
state.output.stderr = False
state.output.aborts = False
state.output.debug = False

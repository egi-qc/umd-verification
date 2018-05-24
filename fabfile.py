# Copyright 2015 Spanish National Research Council
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from fabric.state import output

from umd.products.arc import arc_ce                         	    # NOQA
from umd.products.argus import argus        	                    # NOQA
# from umd.products.argus import argus_puppet       	            # NOQA
# from umd.products.argus import argus_puppet_no_metapkg            # NOQA
# from umd.products.argus import argus_yaim                   	    # NOQA
# from umd.products.argus import ees                          	    # NOQA
from umd.products.bdii import bdii_site              	            # NOQA
# from umd.products.bdii import bdii_top_puppet               	    # NOQA
from umd.products.ca import ca                         	            # NOQA
# from umd.products.canl import canl                          	    # NOQA
from umd.products.caso import caso                          	    # NOQA
from umd.products.clients_solo import clients_solo                  # NOQA
from umd.products.cloud_info_provider import cloud_info_provider    # NOQA
# from umd.products.cream import gridenginerized              	    # NOQA
# from umd.products.cream import standalone                   	    # NOQA
from umd.products.cream import cream                   		    # NOQA
# from umd.products.dcache import dcache                      	    # NOQA
from umd.products.dpm import dpm                     	            # NOQA
from umd.products.frontier_squid import frontier_squid      	    # NOQA
from umd.products.fts import fts                            	    # NOQA
# from umd.products.glexec import glexec_wn                   	    # NOQA
from umd.products.gridftp import gridftp                     	    # NOQA
# from umd.products.gram5 import gram5                        	    # NOQA
# from umd.products.gridsite import gridsite                  	    # NOQA
from umd.products.im import im                  		    # NOQA
from umd.products.individual_packages import individual_packages    # NOQA
from umd.products.keystone_voms import keystone_voms                # NOQA
# from umd.products.keystone_voms import keystone_voms_full         # NOQA
from umd.products.myproxy import myproxy                    	    # NOQA
from umd.products.ooi import ooi                    	            # NOQA
from umd.products.rc import rc                              	    # NOQA
# from umd.products.storm import storm                        	    # NOQA
from umd.products.ui import ui         				    # NOQA
# from umd.products.ui import ui_gfal, gfal_solo              	    # NOQA
# from umd.products.voms import voms_server                   	    # NOQA
# from umd.products.wms import wms_utils                      	    # NOQA
from umd.products.wn import wn                      		    # NOQA
from umd.products.xrootd import xrootd                      	    # NOQA


output.status = False
output.stdout = False
output.warnings = False
output.running = True
output.user = True
output.stderr = False
output.aborts = False
output.debug = False

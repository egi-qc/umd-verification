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

from umd import base


wms_utils = base.Deploy(
    name="wms-utils",
    doc="WMS utils installation",
    metapkg=[
        "glite-wms-brokerinfo-access",
        "glite-wms-brokerinfo-access-devel",
        "glite-wms-brokerinfo-access-doc",
        "glite-wms-brokerinfo-access-lib",
        "glite-wms-ui-api-python",
        "glite-wms-ui-commands",
        "glite-wms-utils-classad",
        "glite-wms-utils-classad-devel",
        "glite-wms-utils-exception",
        "glite-wms-utils-exception-devel",
        "glite-wms-wmproxy-api-cpp",
    ])

wms = base.Deploy(
    name="wms",
    doc="WMS installation",
    metapkg=[
        "glite-wms-common",
        "glite-wms-configuration",
        "glite-wms-core",
        "glite-wms-ice",
        "glite-wms-interface",
        "glite-wms-jobsubmission",
        "glite-wms-purger",
        "glite-wms-ui-api-python",
        "glite-wms-ui-commands",
        "glite-wms-utils-classad",
        "glite-wms-utils-exception",
        "glite-wms-wmproxy-api-cpp",
    ])

lb = base.Deploy(
    name="wms",
    doc="WMS installation",
    metapkg=[
        "emi-lb",
    ])

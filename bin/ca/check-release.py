#!/usr/bin/env python

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

import datetime
import sys
import urllib2
import xml.etree.ElementTree as ET


for repo in sys.argv[1:]:
    url = '/'.join([repo, "meta/ca-policy-egi-core.release"])
    response = urllib2.urlopen(url)
    txt = response.read()
    root = ET.fromstring(txt)
    date = root.find("Date").text
    daysold = (datetime.datetime.strptime(
        date,
        "%Y%m%d") - datetime.datetime.utcnow()).days
    if daysold < 0:
        print("Metadata release date expired %s days ago: %s" % (abs(daysold),
                                                                 date))
        sys.exit(1)
    else:
        print("%s days to metadata release date expiration" % daysold)

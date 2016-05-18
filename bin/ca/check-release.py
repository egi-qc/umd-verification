#!/usr/bin/env python

import datetime
import sys
import urllib2
import xml.etree.ElementTree as ET


for repo in sys.argv[1:]:
    url = '/'.join([repo, "current/meta/ca-policy-egi-core.release"])
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

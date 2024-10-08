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

import re
from io import StringIO

import ldif


def get_gluevalidator_summary(r):
    """Returns a dictionary with the (errors, warnings, info) counters."""
    d = {}
    for line in r.split('\n'):
        m = re.search("(?<=\|).+", line)
        if m:
            d = dict([elem.strip().split('=')
                      for elem in m.group(0).split(';')])
            break
    return d


def ldifize(ldap_result):
    """Writes ldap's query result in LDIF format to the given file."""
    out = StringIO.StringIO()
    for dn, attrs in ldap_result:
        ldif_writer = ldif.LDIFWriter(out)
        ldif_writer.unparse(dn, attrs)
    return out.getvalue()


def validate_version(v):
    try:
        return re.search("^\w+(\.[\w-]+)+$", v).group(0)
    except AttributeError:
        return False

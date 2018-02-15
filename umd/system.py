import platform
import socket

from umd import api

# hostname
fqdn = socket.getfqdn()

distname, version, distid = platform.dist()
distname = distname.lower()
version = version.lower()
distid = distid.lower()

# major & distro version
version_major = version.split('.')[0]
if not version_major.isdigit():
    api.fail("Could not get major OS version for '%s'" % version)
    distro_version = '_'.join(version)
else:
    distro_version = ''.join([distname, version_major]).lower()

if distro_version in [ "centos6" ]:
    distro_version = "redhat6"

import platform
import socket

from umd import exception


# hostname
fqdn = socket.getfqdn()

distname, version, distid = platform.dist()
distname = distname.lower()
version = version.lower()
distid = distid.lower()

# major version
version_major = version.split('.')[0]
if not version_major.isdigit():
    raise exception.InstallException(("Could not get major OS version "
                                      "for '%s'" % version))

# distro_version
distro_version = ''.join([distname, version_major]).lower()

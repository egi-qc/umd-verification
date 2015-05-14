import os.path

from umd.api import runcmd
from umd.base import utils as butils
from umd import exception
from umd import system


def yum(action, pkgs=None):
    if pkgs:
        r = runcmd("yum -y %s %s" % (action, " ".join(pkgs)))
    else:
        r = runcmd("yum -y %s" % action)
    return r


class PkgTool(object):
    PKGTOOL = {
        "redhat": yum,
    }
    REPOPATH = {
        "redhat": "/etc/yum.repos.d/",
    }

    def _enable_repo(self, repofile):
        runcmd("wget %s -O %s" % (repofile,
                                  os.path.join(self.REPOPATH[system.distname],
                                               os.path.basename(repofile))))

    def get_path(self):
        return self.REPOPATH[system.distname]

    def install(self, pkgs, repofile=None):
        if repofile:
            self._enable_repo(repofile)
        return self._exec(action="install", pkgs=pkgs)

    def remove(self, pkgs):
        return self._exec(action="remove", pkgs=pkgs)

    def update(self):
        return self._exec(action="update")

    def _exec(self, action, pkgs=None):
        try:
            if pkgs:
                pkgs = butils.to_list(pkgs)
                return self.PKGTOOL[system.distname](action, pkgs)
            else:
                return self.PKGTOOL[system.distname](action)
        except KeyError:
            raise exception.InstallException("'%s' OS not supported"
                                             % system.distname)

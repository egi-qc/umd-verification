from umd.base import Deploy

from umd.products.glexec import glexec_wn
from umd.products.storm import sl5,sl6
from umd.products.ui import ui
from umd.utils import to_list


# FIXME This should be obtained programatically
def get_metapkg_list():
    l = []
    for pkg in ["cvmfs"]:
        if isinstance(pkg, list):
            l.extend(pkg)
        else:
            l.append(pkg)
    return l


rc = Deploy(
    name="release-candidate",
    doc="Release Candidate probe.",
    metapkg=get_metapkg_list(),
    qc_step="QC_DIST_1",
    dryrun=True)

from umd.base import Deploy

from umd.products.glexec import glexec_wn
from umd.products.storm import sl5,sl6
from umd.products.ui import ui
from umd.utils import to_list


# FIXME This should be obtained programatically
def get_metapkg_list():
    l = []
    for pkgs in (to_list(sl6.metapkg),
                 to_list(glexec_wn.metapkg),
                 to_list(ui.metapkg),
                 ["emi-cream-ce",
                  "apel-client",
                  "apel-lib"]):
        l.extend(pkgs)
    return l


rc = Deploy(
    name="release-candidate",
    doc="Release Candidate probe.",
    metapkg=get_metapkg_list(),
    qc_step="QC_DIST_1",
    dryrun=True)

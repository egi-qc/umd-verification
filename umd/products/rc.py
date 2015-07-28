from umd import base


# FIXME This should be obtained programatically
def get_metapkg_list():
    l = []
    for pkg in ["cvmfs"]:
        if isinstance(pkg, list):
            l.extend(pkg)
        else:
            l.append(pkg)
    return l


rc = base.Deploy(
    name="release-candidate",
    doc="Release Candidate probe.",
    metapkg=get_metapkg_list(),
    qc_step="QC_DIST_1",
    dryrun=True)

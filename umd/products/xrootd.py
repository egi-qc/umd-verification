from umd import base


xrootd = base.Deploy(
    name="xrootd",
    doc="xrootd installation",
    metapkg=[
        "xrootd",
        "xrootd-client",
        "xrootd-client-devel",
        "xrootd-client-libs",
        "xrootd-compat",
        "xrootd-compat-client-libs",
        "xrootd-compat-libs",
        "xrootd-compat-server-libs",
        "xrootd-devel",
        "xrootd-doc",
        "xrootd-fuse",
        "xrootd-libs",
        "xrootd-private-devel",
        "xrootd-python",
        "xrootd-selinux",
        "xrootd-server",
        "xrootd-server-devel",
        "xrootd-server-libs",
    ])

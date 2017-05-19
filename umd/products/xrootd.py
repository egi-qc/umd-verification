from umd import base
from umd.base.configure.puppet import PuppetConfig


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
    ],
    cfgtool=PuppetConfig(
        manifest="xrootd.pp",
        hiera_data="xrootd.yaml",
        module_from_repository=((
            "https://github.com/egi-qc/puppet-xrootd/archive/"
            "umd.tar.gz"), "xrootd"),
        module_from_puppetforge=[
            "puppet-fetchcrl"]))

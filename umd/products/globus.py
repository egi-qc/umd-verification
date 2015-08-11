from umd import base
from umd.base.configure.puppet import PuppetConfig


gridftp = base.Deploy(
    name="globus-gridftp",
    doc="Globus GridFTP server.",
    metapkg="ige-meta-globus-gridftp",
    need_cert=True,
    has_infomodel=False,
    cfgtool=PuppetConfig(
        manifest="gridftp.pp",
        module_from_repository=("hg",
                                "https://code.google.com/p/lutak/")),
    qc_specific_id="globus-gridftp")

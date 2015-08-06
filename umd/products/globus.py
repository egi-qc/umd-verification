from umd import base


gridftp = base.Deploy(
    name="globus-gridftp",
    doc="Globus GridFTP (metapkg: ige-meta-globus-gridftp).",
    metapkg="ige-meta-globus-gridft",
    need_cert=True,
    qc_specific_id="globus-gridftp")

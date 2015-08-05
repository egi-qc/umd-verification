from umd import base


argus = base.Deploy(
    name="argus",
    doc="ARGUS server deployment.",
    metapkg="emi-argus",
    need_cert=True,
    nodetype="ARGUS_server",
    siteinfo=["site-info-ARGUS_server.def"],
    qc_specific_id="argus")

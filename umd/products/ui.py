from umd.base import Deploy


ui = Deploy(
    name="ui",
    doc="User Interface (UI) server deployment.",
    metapkg="emi-ui",
    has_infomodel=False,
    nodetype="UI",
    siteinfo=["site-info-UI.def"],
    qc_specific_id="ui")

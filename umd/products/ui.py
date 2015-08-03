from umd.base import Deploy


ui = Deploy(
    name="ui",
    doc="User Interface server deployment.",
    metapkg="emi-ui",
    has_infomodel=False,
    nodetype="UI",
    siteinfo=["site-info-UI.def"],
    qc_specific_id="ui")

ui_myproxy = Deploy(
    name="myproxy-client",
    doc="MyProxy client testing.",
    metapkg=["emi-ui", "myproxy"],
    has_infomodel=False,
    nodetype="UI",
    siteinfo=["site-info-UI.def"],
    qc_specific_id="myproxy-client")

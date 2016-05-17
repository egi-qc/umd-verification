from umd import base
from umd.base.configure.yaim import YaimConfig


ui = base.Deploy(
    name="ui",
    doc="User Interface server deployment.",
    metapkg="emi-ui",
    cfgtool=YaimConfig(
        nodetype="UI",
        siteinfo=["site-info-UI.def"]),
    qc_specific_id="ui")

ui_myproxy = base.Deploy(
    name="myproxy-client",
    doc="MyProxy client testing.",
    metapkg=["emi-ui", "myproxy"],
    cfgtool=YaimConfig(
        nodetype="UI",
        siteinfo=["site-info-UI.def"]),
    qc_specific_id="myproxy-client")

ui_gfal = base.Deploy(
    name="ui-gfal",
    doc="GFAL2 verfication on UI.",
    metapkg=[
        "emi-ui",
        "gfal2",
        "gfal2-python",
        "gfal2-util",
        "srm-ifce",
        "gfal2-plugin-xrootd"],
    cfgtool=YaimConfig(
        nodetype="UI",
        siteinfo=["site-info-UI.def"]),
    qc_specific_id="ui")

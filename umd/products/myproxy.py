from umd import base
from umd.base.configure.yaim import YaimConfig
from umd import utils


class MyProxyDeploy(base.Deploy):
    def pre_config(self):
        utils.install(["fetch-crl", "glite-px-myproxy-yaim"])


myproxy = MyProxyDeploy(
    name="emi-px",
    doc="MyProxy server deployment.",
    metapkg="myproxy",
    need_cert=True,
    has_infomodel=True,
    cfgtool=YaimConfig(
        nodetype="PX",
        siteinfo=["site-info-PX.def"]),
    qc_specific_id="myproxy")

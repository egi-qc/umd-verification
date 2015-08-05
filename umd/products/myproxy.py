from umd import base
from umd import utils


class MyProxyDeploy(base.Deploy):
    def pre_config(self):
        utils.install(["fetch-crl", "glite-px-myproxy-yaim"])


myproxy = MyProxyDeploy(
    name="myproxy",
    doc="MyProxy server deployment.",
    metapkg="myproxy",
    need_cert=True,
    nodetype="PX",
    siteinfo=["site-info-PX.def"],
    qc_specific_id="myproxy")

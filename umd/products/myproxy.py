from umd.base import Deploy
from umd.utils import install

class MyProxyDeploy(Deploy):
    def pre_config(self):
        install(["fetch-crl", "glite-px-myproxy-yaim"])


myproxy = MyProxyDeploy(
    name="myproxy",
    doc="MyProxy server deployment.",
    metapkg="myproxy",
    need_cert=True,
    nodetype="PX",
    siteinfo=["site-info-PX.def"],
    qc_specific_id="myproxy")

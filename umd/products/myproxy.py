from umd import base
from umd.base.configure.yaim import YaimConfig
from umd import utils


class MyProxyDeploy(base.Deploy):
    def pre_config(self):
        utils.install(["fetch-crl", "glite-px-myproxy-yaim"])


myproxy = MyProxyDeploy(
    name="myproxy",
    doc="MyProxy server deployment.",
    metapkg=["myproxy", "myproxy-server"],
    need_cert=True,
    has_infomodel=True,
    cfgtool=ScriptConfig("bin/myproxy/configure.sh"),
    qc_specific_id="myproxy")

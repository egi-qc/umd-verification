from umd import base
from umd.base.configure.script import ScriptConfig
from umd import utils


class MyProxyDeploy(base.Deploy):
    def pre_config(self):
        utils.install("fetch-crl")


myproxy = MyProxyDeploy(
    name="myproxy",
    doc="MyProxy server deployment.",
    metapkg=["myproxy", "myproxy-server"],
    need_cert=True,
    cfgtool=ScriptConfig("./bin/myproxy/configure.sh"))

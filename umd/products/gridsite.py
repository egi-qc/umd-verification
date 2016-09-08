from umd import base
from umd.base.configure.script import ScriptConfig
from umd import utils



class GridSiteDeploy(base.Deploy):
    def pre_config(self):
        utils.install(["ca-policy-egi-core", "httpd"])


gridsite = GridSiteDeploy(
    name="gridsite",
    doc="Gridsite installation",
    metapkg=[
        "gridsite",
        "gridsite-clients",
        "gridsite-devel",
        "gridsite-doc",
        "gridsite-libs",
        "gridsite1.7-compat",
    ],
    need_cert=True,
    cfgtool=ScriptConfig("./bin/gridsite/configure.sh"),
    qc_specific_id="gridsite")

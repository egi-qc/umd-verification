from umd import base
from umd.base.configure.yaim import YaimConfig


class BDIIDeploy(base.Deploy):
    def post_install(self):
        self.cfgtool.run()


bdii_site = BDIIDeploy(
    name="bdii-site",
    doc="Site BDII deployment.",
    metapkg="emi-bdii-site",
    has_infomodel=True,
    cfgtool=YaimConfig(
        nodetype="BDII_site",
        siteinfo=["site-info-BDII_site.def"]))

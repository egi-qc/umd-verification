from umd import base


class BDIIDeploy(base.Deploy):
    def post_install(self):
        self.cfgtool.run()


bdii_site = BDIIDeploy(
    name="bdii-site",
    doc="Site BDII deployment.",
    metapkg="emi-bdii-site",
    nodetype="BDII_site",
    siteinfo=["site-info-BDII_site.def"])

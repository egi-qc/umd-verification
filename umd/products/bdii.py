from umd import api
from umd import base
from umd.base.configure.puppet import PuppetConfig
from umd.base.configure.yaim import YaimConfig
from umd import config
from umd import system
from umd import utils


class BDIIDeploy(base.Deploy):
    def post_install(self):
        r = config.CFG["cfgtool"].run()
        if r.failed:
            api.fail("Error while running the configuration tool",
                     stop_on_error=True)

    def pre_validate(self):
        # 1. LDAP utils installation
        if system.distname in ["redhat", "centos"]:
            utils.install("openldap-clients")

        # 2. Decrease BDII_BREATHE_TIMEOUT (for validation tests)
        utils.runcmd(("sed -i 's/BDII_BREATHE_TIME=.*/BDII_BREATHE_TIME=10/g' "
                      "/etc/bdii/bdii.conf && /etc/init.d/bdii restart"))


bdii_site_yaim = BDIIDeploy(
    name="bdii-site-yaim",
    doc="Site BDII deployment with YAIM.",
    metapkg="emi-bdii-site",
    has_infomodel=True,
    cfgtool=YaimConfig(
        nodetype="BDII_site",
        siteinfo=["site-info-BDII_site.def"]))

bdii_site_puppet = BDIIDeploy(
    name="bdii-site-puppet",
    doc="Site BDII deployment with Puppet.",
    metapkg="emi-bdii-site",
    cfgtool=PuppetConfig(
        manifest="site_bdii.pp",
        hiera_data="bdii.yaml",
        module_from_puppetforge="CERNOps-bdii"),
    qc_specific_id="bdii")

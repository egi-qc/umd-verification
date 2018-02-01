from umd import base
from umd.base.configure.puppet import PuppetConfig
from umd import config
from umd import utils
from umd.products import utils as product_utils


class CreamCEDeploy(base.Deploy):
    def pre_validate(self):
        utils.install("glite-ce-cream-cli")
        if not config.CFG.get("x509_user_proxy", None):
            # fake proxy
            config.CFG["x509_user_proxy"] = product_utils.create_fake_proxy()
            # fake voms server - lsc
            product_utils.add_fake_lsc()


cream = CreamCEDeploy(
    name="cream",
    need_cert=True,
    has_infomodel=True,
    cfgtool=PuppetConfig(
        manifest="cream.pp",
        hiera_data="cream.yaml",
        module=["git://github.com/egi-qc/puppet-slurm.git",
                "infnpd-creamce",
                "puppetlabs-firewall"]),
    qc_specific_id="cream")

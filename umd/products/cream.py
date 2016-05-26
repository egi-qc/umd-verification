from umd import api
from umd import base
from umd.base.configure.yaim import YaimConfig
from umd import utils


exceptions = {
    "qc_sec_5": {
        "known_worldwritable_filelist":
            ["/var/blah/user_blah_job_registry.bjr/registry.locktest"]}}


class CreamCEStandalone(base.Deploy):
    """CREAM CE standalone deployment (configuration via Yaim)."""
    def pre_config(self):
        api.info("PRE-config actions.")

        utils.install("sudo")

        api.info("<sudo> package installed.")
        api.info("END of PRE-config actions.")


class CreamCEGridengine(base.Deploy):
    """CREAM CE + GridEngine on Scientific Linux deployment."""
    def pre_config(self):
        api.info("PRE-config actions.")

        utils.install(["sudo", "gridengine", "gridengine-qmaster"])

        api.info(("<sudo>, <gridengine> and <gridengine-qmaster> packages "
                  "installed."))
        api.info("END of PRE-config actions.")


standalone = CreamCEStandalone(
    name="creamce-standalone",
    metapkg="emi-cream-ce",
    need_cert=True,
    has_infomodel=True,
    cfgtool=YaimConfig(
        nodetype="creamCE",
        siteinfo=["site-info-creamCE.def"]),
    qc_specific_id="cream",
    exceptions=exceptions)

gridenginerized = CreamCEGridengine(
    name="creamce-gridengine",
    metapkg=["emi-cream-ce",
             "glite-info-dynamic-ge",
             "glite-yaim-ge-utils"],
    need_cert=True,
    has_infomodel=True,
    cfgtool=YaimConfig(
        nodetype=["creamCE", "SGE_utils"],
        siteinfo=["site-info-creamCE.def",
                  "site-info-SGE_utils.def"]),
    qc_specific_id="cream",
    exceptions=exceptions)

lsfized = base.Deploy(
    name="creamce-lsf",
    metapkg=["emi-cream-ce",
             "emi-lsf-utils"])


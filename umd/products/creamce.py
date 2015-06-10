from umd.api import info
from umd.base import Deploy
from umd.utils import install


exceptions = {
    "qc_sec_5": {
        "known_worldwritable_filelist":
            ["/var/blah/user_blah_job_registry.bjr/registry.locktest"]}}


class CreamCEStandalone(Deploy):
    """CREAM CE standalone deployment (configuration via Yaim)."""
    def pre_config(self):
        info("PRE-config actions.")

        install("sudo")

        info("<sudo> package installed.")
        info("END of PRE-config actions.")


class CreamCEGridengine(Deploy):
    """CREAM CE + GridEngine on Scientific Linux deployment (configuration
       via Yaim).
    """
    def pre_config(self):
        info("PRE-config actions.")

        install(["sudo", "gridengine", "gridengine-qmaster"])

        info(("<sudo>, <gridengine> and <gridengine-qmaster> packages "
              "installed."))
        info("END of PRE-config actions.")


standalone = CreamCEStandalone(
    name="creamce-standalone",
    metapkg="emi-cream-ce",
    need_cert=True,
    nodetype="creamCE",
    siteinfo=["site-info-creamCE.def"],
    qc_specific_id="cream",
    exceptions=exceptions)

gridenginerized = CreamCEGridengine(
    name="creamce-gridengine",
    metapkg="emi-cream-ce emi-ge-utils",
    need_cert=True,
    nodetype=["creamCE", "SGE_utils"],
    siteinfo=["site-info-creamCE.def",
              "site-info-SGE_utils.def"],
    qc_specific_id="cream",
    exceptions=exceptions)

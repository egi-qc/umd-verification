from umd import base
from umd.base.configure.yaim import YaimConfig
from umd import utils


class EESDeploy(base.Deploy):
    def pre_validate(self):
        utils.runcmd("useradd -r ees")
        utils.runcmd("/etc/init.d/ees start")
        utils.install("nc")


argus = base.Deploy(
    name="argus",
    doc="ARGUS server deployment.",
    metapkg="emi-argus",
    need_cert=True,
    has_infomodel=True,
    cfgtool=YaimConfig(
        nodetype="ARGUS_server",
        siteinfo=["site-info-ARGUS_server.def"]),
    qc_specific_id="argus")

ees = EESDeploy(
    name="argus-ees",
    doc="ARGUS EES daemon deployment.",
    metapkg="ees",
    qc_specific_id="argus-ees")

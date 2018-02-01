from umd import api
from umd import base
from umd import config
from umd.base.configure.ansible import AnsibleConfig
from umd import system
from umd import utils


class ArcCEAnsibleDeploy(base.Deploy):
    def pre_config(self):
        # extra vars
        extra_vars = [
            "arc_x509_user_key: %s" % config.CFG["cert"].key_path,
            "arc_x509_user_cert: %s" % config.CFG["cert"].cert_path]
        self.cfgtool.extra_vars = extra_vars

arc_ce = ArcCEAnsibleDeploy(
    name="arc-ce",
    doc="ARC computing element server deployment.",
    need_cert=True,
    has_infomodel=True,
    cfgtool=AnsibleConfig(
        role="https://github.com/egi-qc/ansible-arc"),)

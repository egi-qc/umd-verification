from umd import api
from umd import base
from umd.base.configure.ansible import AnsibleConfig
from umd import config


class CADeploy(base.Deploy):
    def format_version(self, version):
        _version = version.replace('.', '/')
        if len(_version.split('/')) != 3:
            api.fail(("CA release version provided has a wrong format: use "
                      "dot '.' separated i.e. '<major>.<minor>.<patch>'"),
                     stop_on_error=True)
        return _version

    def pre_config(self):
        ca_version = config.CFG["ca_version"]
        extra_vars = []
        if ca_version:
            extra_vars = [
                "ca_verification: true",
                "ca_version: %s" % self.format_version(ca_version)]
        else:
            api.info("Installing last available production version")
        if config.CFG["distribution"] == "umd":
            extra_vars.append("crl_deploy: true")
            config.CFG["qc_specific_id"].append("crl")
        self.cfgtool.extra_vars = extra_vars

ca = CADeploy(
    name="ca",
    doc="CA installation using Ansible.",
    cfgtool=AnsibleConfig(
        role="https://github.com/egi-qc/ansible-umd"),
    qc_specific_id=["ca", "crl"])

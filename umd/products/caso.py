from umd import base
from umd.base.configure.ansible import AnsibleConfig
from umd import system

class CasoDeploy(base.Deploy):
    def pre_config(self):
        # extra vars
        extra_vars = [
            "site_name: UMD",
            "projects: demo",
            "mapping_file: /etc/caso/voms.json",
            "extractor: nova",
            "auth_type: password",
            "auth_url: http://%s/identity" % system.ip,
            "username: admin",
            "user_domain_name: default",
            "password: secret",
            "output_path: /var/spool/apel/outgoing/openstack",
            "vos: { \"demo\": [\"demo\"]}"]
        self.cfgtool.extra_vars = extra_vars


caso = CasoDeploy(
    name="caso",
    doc="Accounting parser for OpenStack (caso) deployment using Ansible.",
    cfgtool=AnsibleConfig(
        role="https://github.com/egi-qc/ansible-caso"),
    qc_specific_id="caso")

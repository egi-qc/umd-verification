from umd import base
from umd.base.configure.ansible import AnsibleConfig
from umd import utils


class MyProxyDeploy(base.Deploy):
    def pre_config(self):
        utils.install("fetch-crl")


# argus = ArgusDeploy(
argus = base.Deploy(
    name="myproxy",
    doc="MyProxy server deployment using Ansible.",
    need_cert=True,
    has_infomodel=True,
    cfgtool=AnsibleConfig(
        role="https://github.com/egi-qc/ansible-myproxy"),)

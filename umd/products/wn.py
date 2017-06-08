import os.path

from umd import api
from umd import base
from umd.base.configure.ansible import AnsibleConfig
from umd import config
from umd import system
from umd import utils


#class ArgusDeploy(base.Deploy):
#    def pre_config(self):
#        # extra vars
#        extra_vars = [
#            "pap_host: %s" % system.fqdn,
#            "pap_host_dn: %s" % config.CFG["cert"].subject,
#            "pdp_host: %s" % system.fqdn,
#            "pepd_host: %s" % system.fqdn]
#        self.cfgtool.extra_vars = extra_vars
#
#
#argus = ArgusDeploy(
wn = base.Deploy(
    name="worker-node",
    doc="WN deployment using Ansible.",
    cfgtool=AnsibleConfig(
        role="https://github.com/egi-qc/ansible-wn"),)

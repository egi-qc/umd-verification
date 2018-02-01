from umd import base
from umd.base.configure.ansible import AnsibleConfig
from umd import config


class IndividualDeploy(base.Deploy):
    def pre_config(self):
        # extra vars
        extra_vars = [
            "pkg_list: [%s]" % ','.join(["'%s'" % pkg
                                         for pkg in config.CFG["metapkg"]])]
        self.cfgtool.extra_vars = extra_vars


individual = IndividualDeploy(
    name="individual-packages",
    doc="Individual installation of packages using Ansible.",
    cfgtool=AnsibleConfig(role="https://github.com/egi-qc/ansible-package-install"),)

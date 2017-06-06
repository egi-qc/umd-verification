from umd import base
from umd.base.configure.ansible import AnsibleConfig
from umd import config


class IndividualDeploy(base.Deploy):
    def pre_config(self):
        # extra vars
        extra_vars = [
            "pkg_list: [%s]" % ','.join(["'%s'" % pkg
                                         for pkg in config.CFG["metapkg"]])]
        print(">>>>>>>>>>> METAPKG: ", config.CFG["metapkg"])
        print(">>>>>>>>>>> EXTRA VARS: ", extra_vars)
        self.cfgtool.extra_vars = extra_vars


#individual = base.Deploy(
#    name="individual-packages",
#    doc="Individual installation of packages.",
#    need_cert=True,
#    qc_step=["QC_DIST_1", "QC_FUNC_1"],
#    qc_specific_id="mkgridmap"
#)

individual = IndividualDeploy(
    name="individual-packages",
    doc="Individual installation of packages using Ansible.",
    cfgtool=AnsibleConfig(role="https://github.com/egi-qc/ansible-package-install"),)

import os.path

from umd import base
from umd.base.configure.ansible import AnsibleConfig
from umd import config


class ReleaseCandidateDeploy(base.Deploy):
    def pre_config(self):
        # extra vars
        extra_vars = ["enable_candidate_repo: true",
                      "logfile: %s"
                      % os.path.join(config.CFG["log_path"], "install.log")]
        self.cfgtool.extra_vars = extra_vars

rc = ReleaseCandidateDeploy(
    name="release-candidate",
    doc="Release Candidate validation.",
    cfgtool=AnsibleConfig(
        role="https://github.com/egi-qc/ansible-release-candidate")
)

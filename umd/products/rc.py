import os.path
import re
import urllib2
import xml.etree.ElementTree as ET

from umd import api
from umd import base
from umd.base.configure.ansible import AnsibleConfig
from umd import config
from umd.products import utils as product_utils
from umd import system
from umd import utils


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

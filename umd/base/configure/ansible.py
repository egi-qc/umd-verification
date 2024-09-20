# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os.path

from umd.base.configure import BaseConfig
from umd.base.configure import common
from umd import config
from umd import utils


UMD_VARS_FILE = "/tmp/umd.yaml"
OS_VARS_FILE = "/tmp/os.yaml"


class AnsibleConfig(BaseConfig):
    def __init__(self, role, checkout="master", extra_vars=None, tags="all"):
        """Runs Ansible configurations.

        :role: Galaxy name or GitHub repository where the role is located.
        :checkout: Branch/tag/commit to checkout (see ansible-pull manpage).
        :extra_vars: Extra variables added to Ansible execution (usually
        filled in pre_config()).
        :tags: Run only tasks tagged with this value.
        """
        super(AnsibleConfig, self).__init__()
        self.role = role
        self.checkout = checkout
        self.extra_vars = extra_vars
        self.tags = utils.to_list(tags)

    def _run(self):
        if self.role.find("://") != -1:
            repo_location = os.path.join(
                "/etc/ansible/roles",
                os.path.basename(self.role))
            cmd = "ansible-pull -vvv -C %s -d %s -i %s -U %s" % (
                  self.checkout,
                  repo_location,
                  os.path.join(repo_location, "hosts"),
                  self.role)
            # extra vars
            cmd += " --extra-vars '@%s'" % UMD_VARS_FILE
            if self.extra_vars:
                _extra_vars_file = self._add_extra_vars()
                cmd += " --extra-vars '@%s'" % _extra_vars_file
            # extra vars runtime file
            if config.CFG.get("params_file", None):
                cmd += " --extra-vars '@%s'" % config.CFG["params_file"]
            # tags
            if self.tags:
                cmd += " --tags '%s'" % ','.join(self.tags)

        r = utils.runcmd(cmd,
                         log_to_file="qc_conf",
                         stop_on_error=False,
                         nosudo=True)
        return r

    def config(self, logfile=None):
        # Install ansible if it does not exist
        if utils.runcmd("ansible --help", stop_on_error=False).failed:
            utils.install("ansible")

        # UMD params
        common.set_umd_params(
            "umd_ansible.yaml", UMD_VARS_FILE)
        # OS params
        common.set_os_params(
            "os_ansible.yaml", OS_VARS_FILE)

        # Run ansible
        r = self._run()
        self.has_run = True

        return r

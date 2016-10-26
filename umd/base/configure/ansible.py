import os.path

from umd.base.configure import BaseConfig
from umd import utils


class AnsibleConfig(BaseConfig):
    def __init__(self, role, extra_vars=None):
        """Runs Ansible configurations.

        :role: Galaxy name or GitHub repository where the role is located.
        :extra_vars: Extra variables added to Ansible execution (usually
        filled in pre_config()).
        """
        super(AnsibleConfig, self).__init__()
        self.role = role
        self.extra_vars = extra_vars

    def _run(self):
        if self.role.find("://") != -1:
            repo_location = os.path.join("/tmp", os.path.basename(self.role))
            cmd = "ansible-pull -C master -d %s -i %s -U %s" % (
                  repo_location,
                  os.path.join(repo_location, "hosts"), self.role)
            if self.extra_vars:
                cmd += " -e '%s'" % self.extra_vars
        # else:
        #     cmd = "ansible-galaxy install %s" % self.role

        r = utils.runcmd(cmd,
                         log_to_file="qc_conf",
                         stop_on_error=False)
        return r

    def config(self, logfile=None):
        utils.install("ansible")

        r = self._run()
        self.has_run = True

        return r

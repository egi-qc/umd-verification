import os.path

from umd.base.configure import BaseConfig
from umd import utils


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
            cmd = "ansible-pull -C %s -d %s -i %s -U %s" % (
                  self.checkout,
                  repo_location,
                  os.path.join(repo_location, "hosts"),
                  self.role)
            if self.extra_vars:
                cmd += " -e '%s'" % self.extra_vars
            if self.tags:
                cmd += " --tags '%s'" % ','.join(self.tags)
        # else:
        #     cmd = "ansible-galaxy install %s" % self.role

        r = utils.runcmd(cmd,
                         log_to_file="qc_conf",
                         stop_on_error=False)
        return r

    def config(self, logfile=None):
        if utils.runcmd("ansible", stop_on_error=False).failed:
            utils.install("ansible")

        r = self._run()
        self.has_run = True

        return r

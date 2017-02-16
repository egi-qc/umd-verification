import os.path

from umd.base.configure import BaseConfig
from umd import config
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
        self.extra_vars_yaml_file = "/tmp/umd.yaml"
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
            if self.extra_vars or self.extra_vars_yaml_file:
                cmd += " --extra-vars '@%s'" % self.extra_vars_yaml_file
            if self.tags:
                cmd += " --tags '%s'" % ','.join(self.tags)

        r = utils.runcmd(cmd,
                         log_to_file="qc_conf",
                         stop_on_error=False)
        return r

    def add_extra_vars(self, extra_vars):
        if isinstance(extra_vars, list):
            extra_vars = ' '.join(extra_vars)
        if self.extra_vars:
            self.extra_vars = ' '.join([self.extra_vars, extra_vars])
        else:
            self.extra_vars = extra_vars

    def config(self, logfile=None):
        # Install ansible if it does not exist
        if utils.runcmd("ansible --help", stop_on_error=False).failed:
            utils.install("ansible")

        # Add verification repofiles as extra_vars
        utils.render_jinja(
            "umd_ansible.yaml",
            {
                "distribution": config.CFG["distribution"],
                "repository_file": config.CFG.get("repository_file", None)
            },
            output_file=self.extra_vars_yaml_file)

        # Run ansible
        r = self._run()
        self.has_run = True

        return r

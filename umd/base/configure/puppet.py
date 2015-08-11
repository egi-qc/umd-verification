import os.path

from umd import api
from umd.base.configure import BaseConfig
from umd import config
from umd import utils


class PuppetConfig(BaseConfig):
    def __init__(self,
                 manifest,
                 module_from_puppetforge=[],
                 module_from_repository=[],
                 module_path=[]):
        """Runs Puppet configurations.

        :manifest: Main ".pp" with the configuration to be applied.
        :module_from_puppetforge: list of modules to be installed
                                  (from PuppetForge).
        :module_from_repository: module (repotype, repourl) tuples.
        :module_path: Extra Puppet module locations.
        """
        self.manifest = manifest
        self.module_from_puppetforge = utils.to_list(module_from_puppetforge)
        self.module_from_repository = utils.to_list(module_from_repository)
        self.module_path = utils.to_list(module_path)

    def config(self):
        utils.install("puppet")

        for mod in self.module_from_puppetforge:
            r = utils.runcmd("puppet module install %s" % mod)
            if r.failed:
                api.fail("Error while installing module '%s'" % mod)
        self.module_path.append(*["/etc/puppet/modules"])

        module_loc = []
        for mod in self.module_from_repository:
            dirname = utils.clone_repo(*mod)
            if dirname:
                module_loc.append(dirname)
        self.module_path.append(*module_loc)

        logfile = os.path.join(config.CFG["log_path"], "puppet.log")

        r = utils.runcmd(("puppet apply -l %s --modulepath %s %s "
                          "--detail-exitcodes")
                         % (logfile,
                            ':'.join(self.module_path),
                            os.path.join(
                                config.CFG["puppet_path"],
                                self.manifest)))
        if r.failed:
            api.fail("Puppet execution failed. More information in logs: %s"
                     % logfile, do_abort=True)
        else:
            api.info("Puppet execution ended successfully.")

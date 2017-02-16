import os.path
import shutil

from umd import api
from umd.base.configure import BaseConfig
from umd import config
from umd import system
from umd import utils


class PuppetConfig(BaseConfig):
    def __init__(self,
                 manifest,
                 module=[],
                 hiera_data=[]):
        """Runs Puppet configurations.

        :manifest: Main ".pp" with the configuration to be applied.
        :module: Name of a Forge module or git repository (Puppetfile format).
                 In can be a tuple, containing as a second item either the
                 Forge version or a Git repository valid reference (see
                 Puppetfile)
        :hiera_data: YAML file/s with hiera variables.
        """
        super(PuppetConfig, self).__init__()
        self.manifest = manifest
        self.module = utils.to_list(module)
        self.hiera_data = utils.to_list(hiera_data)
        self.hiera_data_dir = "/etc/puppet/hieradata"
        self.module_path = "/etc/puppet/modules"
        self.puppetfile = "etc/puppet/Puppetfile"
        self.params_files = []
        self.use_rvmsudo = False

    def _deploy(self):
        # Install release package
        if not utils.is_pkg_installed("puppetlabs-release"):
            utils.install_remote(config.CFG["puppet_release"])
        # Install puppet client
        r = utils.install("puppet")
        if r.failed:
            api.fail("Puppet installation failed", stop_on_error=True)
        # Set hiera environment - required before pre_config() method
        if not os.path.exists(self.hiera_data_dir):
            utils.runcmd("mkdir %s" % self.hiera_data_dir)

    def _add_hiera_param_file(self, fname):
        self.params_files.append(fname.split('.')[0])

    def _set_hiera(self):
        """Sets hiera configuration files in place."""
        api.info("Adding hiera parameter files: %s" % self.params_files)
        utils.render_jinja(
            "hiera.yaml",
            {
                "hiera_data_dir": self.hiera_data_dir,
                "params_files": self.params_files,
            },
            output_file=os.path.join("/etc/hiera.yaml"))
        shutil.copy("/etc/hiera.yaml", "/etc/puppet/hiera.yaml")

    def _set_hiera_params(self):
        """Sets hiera parameter files (repository deploy and custom params)."""
        # umd file
        _distribution = config.CFG["distribution"]
        if _distribution == "umd":
            _release = "umd_release"
        elif _distribution == "cmd":
            _release = "cmd_release"
        if config.CFG.get("need_cert", ""):
            _igtf_repo = "true"
        else:
            _igtf_repo = "false"
        _data = {
            "release": config.CFG[_release],
            "distribution": _distribution,
            "repository_file": config.CFG.get("repository_file", ""),
            "openstack_release": config.CFG.get("openstack_release", ""),
            "igtf_repo": _igtf_repo,
        }
        utils.render_jinja(
            "umd.yaml",
            _data,
            output_file=os.path.join(self.hiera_data_dir, "umd.yaml"))
        self._add_hiera_param_file("umd.yaml")
        # custom (static) files
        if self.hiera_data:
            for f in self.hiera_data:
                target = os.path.join(self.hiera_data_dir, f)
                utils.runcmd("cp etc/puppet/%s %s" % (f, target))
                self._add_hiera_param_file(f)

    def _set_puppetfile(self):
        """Processes the list of modules given."""
        puppetfile = "/tmp/Puppetfile"
        # Build dict to be rendered
        d = {}
        for mod in self.module:
            version = None
            if isinstance(mod, tuple):
                mod, version = mod
            mod_name = mod
            extra = {}
            if mod.startswith(("git://", "https://", "http://")):
                mod_name = os.path.basename(mod).split('.')[0]
                extra = {"repourl": mod}
                if version:
                    extra = {"repourl": mod, "ref": version}
            else:
                if version:
                    extra = {"version": version}
            d[mod_name] = extra
        # Render Puppetfile template
        return utils.render_jinja("Puppetfile", {"modules": d}, puppetfile)

    def _install_modules(self):
        """Installs required Puppet modules through librarian-puppet."""
        if utils.runcmd("librarian-puppet",
                        envvars=[("PATH", "$PATH:/usr/local/bin")],
                        nosudo=self.use_rvmsudo,
                        stop_on_error=False).failed:
            utils.runcmd("gem install librarian-puppet",
                         nosudo=self.use_rvmsudo)
        puppetfile = self._set_puppetfile()
        utils.runcmd_chdir(
            "librarian-puppet install --clean --path=%s --verbose"
            % self.module_path,
            os.path.dirname(puppetfile),
            envvars=[("PATH", "$PATH:/usr/local/bin")],
            log_to_file="qc_conf",
            nosudo=True)

    def _run(self):
        logfile = os.path.join(config.CFG["log_path"], "puppet.log")
        module_path = utils.runcmd("puppet config print modulepath",
                                   nosudo=self.use_rvmsudo)

        cmd = ("puppet apply --verbose --debug --modulepath %s %s "
               "--detail-exitcodes") % (module_path, self.manifest)
        r = utils.runcmd(cmd,
                         log_to_file="qc_conf",
                         stop_on_error=False,
                         nosudo=self.use_rvmsudo)
        if r.return_code == 0:
            api.info("Puppet execution ended successfully.")
        elif r.return_code == 2:
            api.info(("Puppet execution ended successfully (some warnings "
                      "though, check logs)"))
            r.failed = False
        else:
            api.fail("Puppet execution failed. More information in logs: %s"
                     % logfile,
                     stop_on_error=True)
            r.failed = True
        return r

    def config(self):
        if system.distro_version == "redhat6":
            self.use_rvmsudo = True

        self.manifest = os.path.join(config.CFG["puppet_path"], self.manifest)

        # Set hiera
        self._set_hiera_params()
        self._set_hiera()

        # Deploy modules
        self._install_modules()

        # Run Puppet
        r = self._run()
        self.has_run = True

        return r

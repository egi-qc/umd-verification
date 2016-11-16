from distutils import version
import itertools
import os.path
import shutil
import tempfile

import string
import yaml

from umd import api
from umd.base.configure import BaseConfig
from umd import config
from umd import system
from umd import utils


class PuppetConfig(BaseConfig):
    def __init__(self,
                 manifest,
                 module,
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
        # umd
        utils.render_jinja(
            "umd.yaml",
            {
                "umd_release": config.CFG["umd_release"],
                "repository_url": config.CFG.get("repository_url", ""),
                "openstack_release": config.CFG.get("openstack_release", ""),
            },
            output_file=os.path.join(self.hiera_data_dir, "umd.yaml"))
        self.params_files.append("umd.yaml")
        # service (static parameter files)
        if self.hiera_data:
            for f in self.hiera_data:
                target = os.path.join(self.hiera_data_dir, f)
                utils.runcmd("cp etc/puppet/%s %s" % (f, target))
                d[":hierarchy"].append(os.path.splitext(f)[0])
                api.info("Service hiera parameters set: %s" % target)
                self.params_files.append(f)

    def _set_puppetfile(self):
        """Processes the list of modules given."""
        puppetfile = "/tmp/Puppetfile"
        # Build dict to be rendered
        d = {}
        for mod in self.module:
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
         utils.runcmd("gem install librarian-puppet")
         puppetfile = self._set_puppetfile()
         utils.runcmd_chdir(
             "librarian-puppet install --path=%s" % self.module_path,
             os.path.dirname(puppetfile),
             log_to_file="qc_conf")

    def _v3_workaround(self):
        # Include hiera functions in Puppet environment
        utils.install("rubygems")
        utils.runcmd("gem install hiera-puppet --install-dir %s"
                     % self.module_path)
        utils.runcmd("mv %s %s" % (os.path.join(self.module_path, "gems/*"),
                                   self.module_path))

    def _run(self):
        logfile = os.path.join(config.CFG["log_path"], "puppet.log")
        module_path = utils.runcmd("puppet config print modulepath")

        cmd = "puppet apply --modulepath %s %s --detail-exitcodes" % (
            module_path,
            self.manifest)
        r = utils.runcmd(cmd,
                         log_to_file="qc_conf",
                         stop_on_error=False)
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

    def config(self, logfile=None):
        self.manifest = os.path.join(config.CFG["puppet_path"], self.manifest)

        r = utils.install("puppet", log_to_file=logfile)
        if r.failed:
            api.fail("Puppet installation failed", stop_on_error=True)

        # Puppet versions <3 workarounds
        puppet_version = utils.runcmd("facter -p puppetversion")
        if puppet_version and (version.StrictVersion(puppet_version)
           < version.StrictVersion("3.0")):
            # self._v3_workaround()
            pkg_url = config.CFG["puppet_release"]
            pkg_loc = "/tmp/puppet-release.rpm"
            r = utils.runcmd("wget %s -O %s" % (pkg_url, pkg_loc))
            if r.failed:
                api.fail("Could not fetch Puppet package from '%s'" % pkg_url,
                         stop_on_error=True)
            else:
                api.info("Fetched Puppet release package from '%s'." % pkg_url)
            utils.install(pkg_loc)
            utils.runcmd(("sed '/enabled=1/a\priority=1' "
                          "/etc/yum.repos.d/puppet*"))

            # FIXME (orviz) Remove this check when dropping redhat5 support
            if system.distro_version == "redhat5":
                pkg = ("ftp://rpmfind.net/linux/centos/5.11/os/x86_64/CentOS/"
                       "virt-what-1.11-2.el5.x86_64.rpm")
                utils.runcmd(("wget %s -O /tmp/virt-what.rpm && yum -y "
                              "install /tmp/virt-what.rpm") % pkg)

            utils.install("puppet")

        # Hiera environment
        if not os.path.exists(self.hiera_data_dir):
            utils.runcmd("mkdir %s" % self.hiera_data_dir)
        self._set_hiera_params()
        self._set_hiera()

        # Deploy modules
        self._install_modules()

        # Run Puppet
        r = self._run()
        self.has_run = True

        return r

from distutils import version
import itertools
import os.path
import shutil

import string
import yaml

from umd import api
from umd.base.configure import BaseConfig
from umd import config
from umd import system
from umd import utils


hiera_config = """
---
:backends:
  - yaml
:yaml:
  :datadir: /etc/puppet/hieradata
:hierarchy:
  - global
"""

hiera_umd = """
umd::release: ${umd_release} 
umd::verification::repofile: ${repository_url}
umd::openstack_release: ${openstack_release}
"""


class PuppetConfig(BaseConfig):
    def __init__(self,
                 manifest,
                 hiera_data=[],
                 module_from_puppetforge=[],
                 module_from_repository=[]):
        """Runs Puppet configurations.

        :manifest: Main ".pp" with the configuration to be applied.
        :hiera_data: YAML file/s with hiera variables.
        :module_from_puppetforge: list of modules to be installed
                                  (from PuppetForge).
        :module_from_repository: URL pointing to repository tarball/s.
        """
        super(PuppetConfig, self).__init__()
        self.manifest = manifest
        self.hiera_data = utils.to_list(hiera_data)
        self.hiera_data_dir = "/etc/puppet/hieradata"
        self.module_path = "/etc/puppet/modules"
        self.module_from_puppetforge = utils.to_list(module_from_puppetforge)
        self.module_from_repository = utils.to_list(module_from_repository)
        self.umd_module = "https://github.com/egi-qc/puppet-umd/archive/master.tar.gz"

    def _module_install(self, mod):
        mod_name = ''
        from_repo = False
        if len(mod) == 2:
            mod, mod_name = mod
        if mod.startswith("http"):
            from_repo = True
            dest = os.path.join("/tmp", os.path.basename(mod))
            r = utils.runcmd("wget %s -O %s" % (mod, dest))
            if r.failed:
                api.fail("Could not download tarball '%s'" % mod,
                         stop_on_error=True)
            mod = dest
        r = utils.runcmd("puppet module install %s --force" % mod,
                         stop_on_error=False)
        if r.failed and from_repo:
            r = self._module_install_from_tarball(mod, mod_name)
        if r.failed:
            api.fail("Puppet module '%s' could not be installed" % mod)

    def _module_install_from_tarball(self, tarball, mod_name=''):
        """Installs a Puppet module tarball manually."""
        root_dir = utils.runcmd("tar tzf %s | sed -e 's@/.*@@' | uniq"
                                % tarball)
        dest = os.path.join(self.module_path, root_dir)
        utils.runcmd("tar xvfz %s -C %s" % (tarball, self.module_path))
        if mod_name:
            dest_o = os.path.join(self.module_path, mod_name)
            if os.path.exists(dest_o):
                utils.runcmd("rm -rf %s" % dest_o)
            return utils.runcmd("mv %s %s" % (dest, dest_o))

    def _install_umd_module(self):
        """Installs puppet-umd module in the system."""
        self._module_install(self.umd_module, "umd")    

    def _set_hiera(self):
        """Sets hiera configuration files in place."""
        d = yaml.safe_load(hiera_config)
        with open("/etc/puppet/hiera.yaml", 'w') as f:
            f.write(yaml.dump(d, default_flow_style=False))
        shutil.copy("/etc/puppet/hiera.yaml", "/etc/hiera.yaml")
        if not os.path.exists(self.hiera_data_dir):
            utils.runcmd("mkdir %s" % self.hiera_data_dir)

    def _set_hiera_params(self):
        """Sets hiera parameter files (repository deploy and custom params)."""
        # umd parameter file
        umd_conf = string.Template(hiera_umd).safe_substitute({
            "umd_release": config.CFG["umd_release"],
            "repository_url": config.CFG.get("repository_url", ""),
            "openstack_release": config.CFG.get("openstack_release", ""),
        })
        umd_conf_file = os.path.join(self.hiera_data_dir, "umd.yaml")
        with open(umd_conf_file, 'w') as f:
            f.write(umd_conf)
        api.info("UMD hiera parameters set: %s" % umd_conf_file) 
        # service parameter files
        if self.hiera_data:
            for f in self.hiera_data:
                target = os.path.join(self.hiera_data_dir, f)
                utils.runcmd("cp etc/puppet/%s %s" % (f, target))
                d[":hierarchy"].append(os.path.splitext(f)[0])
                api.info("Service hiera parameters set: %s" % target)

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

        for module in itertools.chain(self.module_from_puppetforge,
                                      self.module_from_repository):
            self._module_install(module)

        # Hiera environment
        self._install_umd_module()
        self._set_hiera()
        self._set_hiera_params()

        # Run Puppet
        r = self._run()
        self.has_run = True

        return r

    def install_module_from_tarball(self, tarball, module_name):
        """Downloads and installs manually a Puppet module tarball."""
        dest_basename = os.path.basename(tarball)
        dest = os.path.join("/tmp", dest_basename)
        utils.runcmd("wget %s -O %s" % (tarball, dest))
        root_dir = utils.runcmd("tar tzf %s | sed -e 's@/.*@@' | uniq" % dest)
        utils.runcmd("tar xvfz %s -C %s" % (dest, self.module_path))
        utils.runcmd("mv %s %s" % (
            os.path.join(self.module_path, root_dir),
            os.path.join(self.module_path, module_name)))

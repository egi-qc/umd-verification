import os.path

from umd import api
from umd import base
from umd.base.configure.puppet import PuppetConfig
from umd import config
from umd.products import voms
from umd import utils


class KeystoneVOMSDeploy(base.Deploy):
    def __init__(self, *args, **kwargs):
        name = "keystone-voms"
        package = "python-keystone-voms"
        description = "Keystone VOMS module"

        name_short = self.version_codename.lower()
        name = "keystone-voms-%s" % name_short
        package = "python-keystone-voms=%s*" % self.version
        description = "Keystone %s VOMS Module (%s)" % (self.version_codename,
                                                        self.version)
        super(KeystoneVOMSDeploy, self).__init__(
            name=name,
            doc=description,
            metapkg=package,
            need_cert=True,
            cfgtool=self.puppetconf,
            qc_specific_id="keystone-voms"
        )

    def pre_install(self):
        utils.enable_repo("cloud-archive:%s"
                          % self.version_codename.lower())

    def pre_config(self):
        # Trust UMDVerificationCA
        ca_location = config.CFG["ca"].location
        if not ca_location:
            ca_location = "/etc/grid-security/certificates/0d2a3bdd.0"
            api.info("Using hardcoded CA path: %s" % ca_location)
        ca_location_basename = os.path.basename(ca_location)
        ca_location_basename_crt = '.'.join([
            ca_location_basename.split('.')[0], "crt"])
        utils.runcmd("cp %s /usr/share/ca-certificates/%s" % (
            ca_location,
            ca_location_basename_crt))
        utils.runcmd("echo '%s' >> /etc/ca-certificates.conf"
                     % ca_location_basename_crt)
        utils.runcmd("update-ca-certificates")
        # pytz requirement for Juno
        if self.version_codename == "Kilo":
            utils.runcmd("pip install pytz==2013.6")

    def pre_validate(self):
        voms.client_install()
        utils.runcmd("pip install voms-auth-system-openstack")


class KeystoneVOMSJunoDeploy(KeystoneVOMSDeploy):
    version = "2014.2"
    version_codename = "Juno"
    puppetconf = PuppetConfig(
        manifest="keystone_voms.pp",
        hiera_data="voms.yaml",
        module_from_puppetforge=[
            "puppetlabs-mysql",
            "puppetlabs/apache --version '>=1.0.0 <2.0.0'",
            "puppetlabs/inifile --version '>=1.0.0 <2.0.0'",
            "puppetlabs/stdlib --version '>=4.0.0 <5.0.0'",
            "puppetlabs/concat --version '>= 1.1.1 < 3.0.0'",
            "stackforge/openstacklib --version '>=5.0.0 <6.0.0'",
            "lcgdm-voms"],
        module_from_repository=((
            "https://github.com/egi-qc/puppet-keystone/archive/"
            "umd_stable_%s.tar.gz" % version_codename.lower()), "keystone")
    )


class KeystoneVOMSKiloDeploy(KeystoneVOMSDeploy):
    version = "2015.1"
    version_codename = "Kilo"
    puppetconf = PuppetConfig(
        manifest="keystone_voms.pp",
        hiera_data="voms.yaml",
        module_from_puppetforge=[
            # "openstack/keystone --version '>=6.0.0 <7.0.0'",
            "openstack/openstacklib --version '>=6.0.0 <7.0.0'",
            "puppetlabs/inifile --version '>=1.0.0 <2.0.0'",
            "puppetlabs-mysql",
            "puppetlabs/apache --version '>=1.0.0 <2.0.0'",
            "puppetlabs-stdlib",
            "puppetlabs/concat",
            "lcgdm-voms"],
        module_from_repository=((
            "https://github.com/egi-qc/puppet-keystone/archive/"
            "umd_stable_%s.tar.gz" % version_codename.lower()), "keystone")
    )


keystone_voms_juno = KeystoneVOMSJunoDeploy()
keystone_voms_kilo = KeystoneVOMSKiloDeploy()

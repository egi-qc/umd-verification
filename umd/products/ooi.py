import os.path

from umd import api
from umd import base
from umd.base.configure.puppet import PuppetConfig
#from umd.common import pki
from umd import config
#from umd.products import utils as product_utils
#from umd.products import voms
#from umd import system
from umd import utils


#class KeystoneVOMSDeploy(base.Deploy):
#    def __init__(self, *args, **kwargs):
#        name = "keystone-voms-%s" % self.version_codename.lower()
#        package = ("python-keystone-voms", self.version + '*')
#        description = "Keystone %s VOMS Module (%s)" % (self.version_codename,
#                                                        self.version)
#        puppetconf = PuppetConfig(
#            manifest="keystone_voms.pp",
#            hiera_data="voms.yaml",
#            module_from_puppetforge=[
#                "openstack/openstacklib",
#                "puppetlabs/inifile",
#                "puppetlabs-mysql",
#                "puppetlabs/apache",
#                "puppetlabs-stdlib",
#                "puppetlabs/concat",
#                "lcgdm-voms"],
#            module_from_repository=((
#                "https://github.com/egi-qc/puppet-keystone/archive/"
#                "umd_stable_%s.tar.gz" % self.version_codename.lower()),
#                "keystone")
#        )
#
#        super(KeystoneVOMSDeploy, self).__init__(
#            name=name,
#            doc=description,
#            metapkg=package,
#            need_cert=True,
#            cfgtool=puppetconf,
#            qc_specific_id="keystone-voms"
#        )
#
#    def pre_install(self):
#        product_utils.add_openstack_distro_repos(self.version_codename.lower())
#
#    def pre_config(self):
#        # Trust UMDVerificationCA
#        ca_location = config.CFG["ca"].location
#        if not ca_location:
#            ca_location = "/etc/grid-security/certificates/0d2a3bdd.0"
#            api.info("Using hardcoded CA path: %s" % ca_location)
#        pki.trust_ca(ca_location)
#        # pytz requirement for Kilo
#        if self.version_codename == "Kilo":
#            utils.runcmd("pip install pytz==2013.6")
#        if system.distname == "centos":
#            # Fix no operatingsystemrelease fact on CentOS 7
#            utils.runcmd("ln -s -f /etc/centos-release /etc/redhat-release")
#            # selinux
#            utils.install("openstack-selinux")
#        elif system.distname == "ubuntu":
#            # utils.runcmd("pip install pbr==0.10.0 mock==1.0.1")
#            utils.runcmd("pip install mock==1.0.1")
#
#    def pre_validate(self):
#        # voms packages
#        voms.client_install()
#        utils.runcmd("pip install voms-auth-system-openstack")
#        # fake proxy
#        product_utils.create_fake_proxy()
#        # fake voms server - lsc
#        product_utils.add_fake_lsc()
#
#
#class KeystoneVOMSJunoDeploy(KeystoneVOMSDeploy):
#    version = "2014.2"
#    version_codename = "Juno"
#
#
#class KeystoneVOMSKiloDeploy(KeystoneVOMSDeploy):
#    version = "2015.1"
#    version_codename = "Kilo"
#
#
#class KeystoneVOMSLibertyDeploy(KeystoneVOMSDeploy):
#    version = "8.0.6"
#    version_codename = "Liberty"
#
#
#class KeystoneVOMSMitakaDeploy(KeystoneVOMSDeploy):
#    version = "9.0.3"
#    version_codename = "Mitaka"
#
#
#keystone_voms_juno = KeystoneVOMSJunoDeploy()
#keystone_voms_kilo = KeystoneVOMSKiloDeploy()
#keystone_voms_liberty = KeystoneVOMSLibertyDeploy()
#keystone_voms_mitaka = KeystoneVOMSMitakaDeploy()


class OOIDeploy(base.Deploy):
    def pre_config(self):
        ooi_params = "ooi::openstack_version: %s" % config.CFG["openstack_release"]
        ooi_conf = os.path.join(config.CFG["cfgtool"].hiera_data_dir,
                                "ooi.yaml")
        if utils.to_yaml(ooi_conf, ooi_params):
            api.info("OOI hiera parameters set: %s" % ooi_conf)
        # Add it to hiera.yaml
        config.CFG["cfgtool"]._add_hiera_param_file("ooi.yaml")


ooi = OOIDeploy(
    name="ooi",
    doc="OCCI OpenStack Interface.",
    cfgtool=PuppetConfig(
        manifest="ooi.pp",
        module=("git://github.com/egi-qc/puppet-ooi.git", "umd"),
    ),
    #qc_specific_id="ooi",
)

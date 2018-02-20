from umd import base
from umd.base.configure.puppet import PuppetConfig
from umd import utils


class DPMDeploy(base.Deploy):
    def pre_config(self):
        dteam_dn = ("/DC=org/DC=terena/DC=tcs/C=ES/O=Consejo Superior de "
                    "Investigaciones Cientificas/CN=PABLO ORVIZ FERNANDEZ "
                    "594361@csic.es")
        utils.write_to_file("/etc/lcgdm-mapfile",
                            dteam_dn,
                            mode='w')

dpm = DPMDeploy(
    name="dpm",
    doc="DPM deployment using Puppet.",
    need_cert=True,
    cfgtool=PuppetConfig(
        manifest="dpm.pp",
        module=[
            "puppetlabs-stdlib",
            "git://github.com/egi-qc/puppet-dpm.git",
            #"git://github.com/cern-it-sdc-id/puppet-dpm",
            ]),
)

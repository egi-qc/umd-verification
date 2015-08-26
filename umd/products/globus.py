from umd import base
from umd.base.configure.puppet import PuppetConfig
from umd import config
from umd import utils


class GridFTPDeploy(base.Deploy):
    def pre_validate(self):
        utils.install("myproxy")

        # FIXME(orviz) 'umd' account hardcoded here
        utils.runcmd("echo '%s umd' > /etc/grid-security/grid-mapfile"
                     % config.CFG["cert"].subject)


gridftp = GridFTPDeploy(
    name="globus-gridftp",
    doc="Globus GridFTP server.",
    metapkg="ige-meta-globus-gridftp",
    need_cert=True,
    cfgtool=PuppetConfig(
        manifest="gridftp.pp",
        hiera_data="gridftp.yaml",
        module_from_puppetforge="lcgdm-gridftp"),
    qc_specific_id="gridftp")

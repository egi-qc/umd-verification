from umd import base
from umd.base.configure.puppet import PuppetConfig
from umd.products import utils as product_utils
from umd.products import voms
from umd import utils


class GridFTPDeploy(base.Deploy):
    def pre_validate(self):
        # voms packages
        #utils.install(["myproxy", "globus-gass-copy-progs", "voms-clients"])
        voms.client_install()
        # fake proxy
        product_utils.create_fake_proxy()
        # fake voms server - lsc
        product_utils.add_fake_lsc()


gridftp = GridFTPDeploy(
    name="gridftp",
    doc="Globus GridFTP server deployment using Puppet.",
    need_cert=True,
    cfgtool=PuppetConfig(
        manifest="gridftp.pp",
        hiera_data="gridftp.yaml",
        module=("git://github.com/cern-it-sdc-id/puppet-gridftp", "master"),
    ),
    qc_specific_id="gridftp")

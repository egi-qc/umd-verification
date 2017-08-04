from umd import base
from umd.base.configure.puppet import PuppetConfig


cream = base.Deploy(
    name="cream",
    need_cert=True,
    has_infomodel=True,
    cfgtool=PuppetConfig(
        manifest="cream.pp",
        hiera_data="cream.yaml",
        module=["git://github.com/cernops/puppet-slurm.git",
                "infnpd-creamce",
                "puppetlabs-firewall"]))

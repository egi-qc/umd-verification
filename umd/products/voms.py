from umd import base
from umd import utils


def client_install():
    utils.install([
        "voms-clients",
        "myproxy"
    ])

voms_server = base.Deploy(
    name="voms-mysql",
    doc="MySQL VOMS server deployment.",
    metapkg="emi-voms-mysql",
    need_cert=True,
    has_infomodel=True)

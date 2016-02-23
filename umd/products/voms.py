from umd import utils


def client_install():
    utils.install([
        "voms-clients",
        "myproxy"
    ])

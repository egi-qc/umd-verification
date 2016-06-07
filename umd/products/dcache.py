from umd import base


dcache = base.Deploy(
    name="dcache",
    doc="dCache installation only.",
    metapkg=[
        "dcache",
        "dcache-srmclient"])

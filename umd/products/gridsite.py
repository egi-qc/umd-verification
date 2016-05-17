from umd import base


gridsite = base.Deploy(
    name="gridsite",
    doc="Gridsite installation",
    metapkg=[
        "gridsite",
        "gridsite-clients",
        "gridsite-devel",
        "gridsite-doc",
        "gridsite-libs",
        "gridsite1.7-compat",
    ])

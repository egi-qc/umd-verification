from umd import base


wms_utils = base.Deploy(
    name="wms-utils",
    doc="WMS utils installation",
    metapkg=[
        "glite-wms-brokerinfo-access",
        "glite-wms-brokerinfo-access-devel",
        "glite-wms-brokerinfo-access-doc",
        "glite-wms-brokerinfo-access-lib",
        "glite-wms-ui-api-python",
        "glite-wms-ui-commands",
        "glite-wms-utils-classad",
        "glite-wms-utils-classad-devel",
        "glite-wms-utils-exception",
        "glite-wms-utils-exception-devel",
        "glite-wms-wmproxy-api-cpp",
    ])

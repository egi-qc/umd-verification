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

wms = base.Deploy(
    name="wms",
    doc="WMS installation",
    metapkg=[
        "glite-wms-common",
        #"glite-wms-common-devel",
        "glite-wms-configuration",
        "glite-wms-core",
        #"glite-wms-core-devel",
        "glite-wms-ice",
        "glite-wms-interface",
        "glite-wms-jobsubmission",
        #"glite-wms-jobsubmission-devel",
        "glite-wms-purger",
        #"glite-wms-purger-devel",
        "glite-wms-ui-api-python",
        "glite-wms-ui-commands",
        "glite-wms-utils-classad",
        #"glite-wms-utils-classad-devel",
        "glite-wms-utils-exception",
        #"glite-wms-utils-exception-devel",
        "glite-wms-wmproxy-api-cpp",
    ])

lb = base.Deploy(
    name="wms",
    doc="WMS installation",
    metapkg=[
        "emi-lb",
    ])

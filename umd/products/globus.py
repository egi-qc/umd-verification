from umd import base
from umd.base.configure.puppet import PuppetConfig
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


gridftp_pkgs = [
    "globus-authz",
    "globus-authz-callout-error",
    "globus-authz-callout-error-devel",
    "globus-authz-callout-error-doc",
    "globus-authz-devel",
    "globus-authz-doc",
    "globus-callout",
    "globus-callout-devel",
    "globus-callout-doc",
    "globus-common",
    "globus-common-devel",
    "globus-common-doc",
    "globus-common-progs",
    "globus-ftp-client",
    "globus-ftp-client-devel",
    "globus-ftp-client-doc",
    "globus-ftp-control",
    "globus-ftp-control-devel",
    "globus-ftp-control-doc",
    "globus-gass-cache",
    "globus-gass-cache-devel",
    "globus-gass-cache-doc",
    "globus-gass-cache-program",
    "globus-gass-copy",
    "globus-gass-copy-devel",
    "globus-gass-copy-doc",
    "globus-gass-copy-progs",
    "globus-gass-server-ez",
    # "globus-gass-server-ez-devel",
    "globus-gass-server-ez-progs",
    "globus-gass-transfer",
    "globus-gass-transfer-devel",
    "globus-gass-transfer-doc",
    "globus-gfork",
    "globus-gfork-devel",
    "globus-gfork-progs",
    "globus-gridftp-server",
    "globus-gridftp-server-control",
    "globus-gridftp-server-control-devel",
    "globus-gridftp-server-progs",
    "globus-gridmap-callout-error",
    "globus-gridmap-callout-error-devel",
    "globus-gridmap-callout-error-doc",
    "globus-gridmap-eppn-callout",
    "globus-gridmap-verify-myproxy-callout",
    "globus-gsi-callback",
    "globus-gsi-callback-devel",
    "globus-gsi-callback-doc",
    "globus-gsi-cert-utils",
    "globus-gsi-cert-utils-devel",
    "globus-gsi-cert-utils-doc",
    "globus-gsi-cert-utils-progs",
    "globus-gsi-credential",
    "globus-gsi-credential-devel",
    "globus-gsi-credential-doc",
    "globus-gsi-openssl-error",
    "globus-gsi-openssl-error-devel",
    "globus-gsi-openssl-error-doc",
    "globus-gsi-proxy-core",
    "globus-gsi-proxy-core-devel",
    "globus-gsi-proxy-core-doc",
    "globus-gsi-proxy-ssl",
    "globus-gsi-proxy-ssl-devel",
    "globus-gsi-proxy-ssl-doc",
    "globus-gsi-sysconfig",
    "globus-gsi-sysconfig-devel",
    "globus-gsi-sysconfig-doc",
    "globus-gss-assist",
    "globus-gss-assist-devel",
    "globus-gss-assist-doc",
    "globus-gss-assist-progs",
    "globus-gssapi-error",
    "globus-gssapi-error-devel",
    "globus-gssapi-error-doc",
    "globus-gssapi-gsi",
    "globus-gssapi-gsi-devel",
    "globus-gssapi-gsi-doc",
    "globus-io",
    "globus-io-devel",
    "globus-openssl-module",
    "globus-openssl-module-devel",
    "globus-openssl-module-doc",
    "globus-proxy-utils",
    "globus-usage",
    "globus-usage-devel",
    "globus-xio",
    "globus-xio-devel",
    "globus-xio-doc",
    "globus-xio-gridftp-driver",
    "globus-xio-gridftp-driver-devel",
    "globus-xio-gridftp-driver-doc",
    "globus-xio-gridftp-multicast",
    "globus-xio-gridftp-multicast-devel",
    "globus-xio-gsi-driver",
    "globus-xio-gsi-driver-devel",
    "globus-xio-gsi-driver-doc",
    "globus-xio-net-manager-driver",
    "globus-xio-net-manager-driver-devel",
    "globus-xio-pipe-driver",
    "globus-xio-pipe-driver-devel",
    "globus-xio-popen-driver",
    "globus-xio-popen-driver-devel",
    "globus-xio-rate-driver",
    "globus-xio-rate-driver-devel",
    "globus-xio-udt-driver",
    "globus-xio-udt-driver-devel",
    "globus-xioperf",
]

default_security_pkgs = [
    "globus-callout",
    "globus-callout-devel",
    "globus-callout-doc",
    "globus-common",
    "globus-common-devel",
    "globus-common-doc",
    "globus-common-progs",
    "globus-usage",
    "globus-usage-devel",
    "globus-authz",
    "globus-authz-callout-error",
    "globus-authz-callout-error-devel",
    "globus-authz-callout-error-doc",
    "globus-authz-devel",
    "globus-authz-doc",
    "globus-gridmap-callout-error",
    "globus-gridmap-callout-error-devel",
    "globus-gridmap-callout-error-doc",
    "globus-gridmap-eppn-callout",
    "globus-gridmap-verify-myproxy-callout",
    "globus-gsi-callback",
    "globus-gsi-callback-devel",
    "globus-gsi-callback-doc",
    "globus-gsi-cert-utils",
    "globus-gsi-cert-utils-devel",
    "globus-gsi-cert-utils-doc",
    "globus-gsi-cert-utils-progs",
    "globus-gsi-credential",
    "globus-gsi-credential-devel",
    "globus-gsi-credential-doc",
    "globus-gsi-openssl-error",
    "globus-gsi-openssl-error-devel",
    "globus-gsi-openssl-error-doc",
    "globus-gsi-proxy-core",
    "globus-gsi-proxy-core-devel",
    "globus-gsi-proxy-core-doc",
    "globus-gsi-proxy-ssl",
    "globus-gsi-proxy-ssl-devel",
    "globus-gsi-proxy-ssl-doc",
    "globus-gsi-sysconfig",
    "globus-gsi-sysconfig-devel",
    "globus-gsi-sysconfig-doc",
    "globus-gssapi-error",
    "globus-gssapi-error-devel",
    "globus-gssapi-error-doc",
    "globus-gssapi-gsi",
    "globus-gssapi-gsi-devel",
    "globus-gssapi-gsi-doc",
    "globus-gss-assist",
    "globus-gss-assist-devel",
    "globus-gss-assist-doc",
    "globus-gss-assist-progs",
    "globus-openssl-module",
    "globus-openssl-module-devel",
    "globus-openssl-module-doc",
    "globus-proxy-utils",
    "globus-io",
    "globus-io-devel",
    "globus-xio",
    "globus-xio-devel",
    "globus-xio-doc",
    "globus-xio-gridftp-driver",
    "globus-xio-gridftp-driver-devel",
    "globus-xio-gridftp-driver-doc",
    "globus-xio-gridftp-multicast",
    "globus-xio-gridftp-multicast-devel",
    "globus-xio-gsi-driver-devel",
    "globus-xio-gridftp-driver-devel",
    "globus-xio-gsi-driver",
    "globus-xio-gsi-driver-devel",
    "globus-xio-gsi-driver-doc",
    "globus-xio-net-manager-driver",
    "globus-xio-net-manager-driver-devel",
    "globus-xio-pipe-driver",
    "globus-xio-pipe-driver-devel",
    "globus-xio-popen-driver",
    "globus-xio-popen-driver-devel",
    "globus-xio-rate-driver",
    "globus-xio-rate-driver-devel",
    "globus-xio-udt-driver",
    "globus-xio-udt-driver-devel",
    "globus-xioperf",
]


gridftp = GridFTPDeploy(
    name="globus-gridftp",
    doc="Globus GridFTP server.",
    # metapkg="ige-meta-globus-gridftp",
    metapkg=gridftp_pkgs,
    need_cert=True,
    cfgtool=PuppetConfig(
        manifest="gridftp.pp",
        hiera_data="gridftp.yaml",
        module_from_repository=(("https://github.com/cern-it-sdc-id/"
                                 "puppet-gridftp/archive/master.tar.gz"),
                                "gridftp")),
    qc_specific_id="gridftp")

default_security = base.Deploy(
    name="globus-default-security",
    doc="Globus default security.",
    metapkg=default_security_pkgs)

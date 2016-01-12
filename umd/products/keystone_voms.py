from umd import base
from umd.base.configure.puppet import PuppetConfig
from umd import utils


apache_conf = """
Listen 5000
WSGIDaemonProcess keystone user=keystone group=nogroup processes=8 threads=1
<VirtualHost _default_:5000>
    LogLevel     warn
    ErrorLog    ${APACHE_LOG_DIR}/error.log
    CustomLog   ${APACHE_LOG_DIR}/ssl_access.log combined

    SSLEngine               on
    SSLCertificateFile      /etc/grid-security/hostcert.pem
    SSLCertificateKeyFile   /etc/grid-security/hostkey.pem
    SSLCACertificatePath    /etc/grid-security/certificates
    SSLCARevocationPath     /etc/grid-security/certificates
    SSLVerifyClient         optional
    SSLVerifyDepth          10
    SSLProtocol             all -SSLv2
    SSLCipherSuite          ALL:!ADH:!EXPORT:!SSLv2:RC4+RSA:+HIGH:+MEDIUM:+LOW
    SSLOptions              +StdEnvVars +ExportCertData

    WSGIScriptAlias /  /usr/lib/cgi-bin/keystone/main
    WSGIProcessGroup keystone
</VirtualHost>

Listen 35357
WSGIDaemonProcess keystoneapi user=keystone group=nogroup processes=8 threads=1
<VirtualHost _default_:35357>
    LogLevel    warn
    ErrorLog    ${APACHE_LOG_DIR}/error.log
    CustomLog   ${APACHE_LOG_DIR}/ssl_access.log combined

    SSLEngine               on
    SSLCertificateFile      /etc/grid-security/hostcert.pem
    SSLCertificateKeyFile   /etc/grid-security/hostkey.pem
    SSLCACertificatePath    /etc/grid-security/certificates
    SSLCARevocationPath     /etc/grid-security/certificates
    SSLVerifyClient         optional
    SSLVerifyDepth          10
    SSLProtocol             all -SSLv2
    SSLCipherSuite          ALL:!ADH:!EXPORT:!SSLv2:RC4+RSA:+HIGH:+MEDIUM:+LOW
    SSLOptions              +StdEnvVars +ExportCertData

    WSGIScriptAlias     / /usr/lib/cgi-bin/keystone/admin
    WSGIProcessGroup    keystoneapi
</VirtualHost>
"""


class KeystoneVOMSDeploy(base.Deploy):
    def __init__(self, *args, **kwargs):
        name = "keystone-voms"
        package = "python-keystone-voms"
        description = "Keystone VOMS module"

        name = "keystone-voms-%s" % self.version_codename.lower()
        package = "python-keystone-voms=%s*" % self.version
        description = "Keystone %s VOMS Module (%s)" % (self.version_codename,
                                                        self.version)

        super(KeystoneVOMSDeploy, self).__init__(
            name=name,
            doc=description,
            metapkg=package,
            need_cert=True,
            cfgtool=PuppetConfig(
                manifest="keystone_voms.pp",
                # hiera_data="gridftp.yaml",
                module_from_puppetforge=["puppetlabs-mysql",
                                         "puppetlabs-keystone"]),
            # qc_specific_id="gridftp"
        )

    def pre_install(self):
        utils.enable_repo("cloud-archive:%s"
                          % self.version_codename.lower())

    def post_config(self):
        deps = ["apache2", "apache2-mpm-prefork", "libapache2-mod-wsgi",
                "libvomsapi1"]
        utils.install(deps)

        utils.runcmd("rm -f /etc/apache2/sites-enabled/*")
        with open("/etc/apache2/sites-enabled/keystone", 'w') as f:
            f.write(apache_conf)
            f.flush()


class KeystoneVOMSJunoDeploy(KeystoneVOMSDeploy):
    version = "2014.2"
    version_codename = "Juno"


keystone_voms_juno = KeystoneVOMSJunoDeploy()

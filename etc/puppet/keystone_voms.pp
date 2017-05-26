class { "umd": igtf_repo => "yes" }

## Keystone VOMS ##

if $::osfamily == "Debian" {
    $apache_srv = "apache2"
    $pkg = "python-keystone-voms"
}
else {
    $apache_srv = "httpd"
    $pkg = "python-keystone_voms"
}
exec {
    "reload":
        command => "/usr/sbin/service ${apache_srv} reload",
        refreshonly => true,
}

package { $pkg: ensure => latest }

# keystone-paste.ini
ini_setting {
    "VOMS_filter":
        ensure  => present,
        path    => "/etc/keystone/keystone-paste.ini",
        section => "filter:voms",
        setting => "paste.filter_factory",
        value   => "keystone_voms.core:VomsAuthNMiddleware.factory",
}

ini_subsetting {
    "VOMS_filter_public_api":
        ensure            => present,
        section           => "pipeline:public_api",
        setting           => "pipeline",
        key_val_separator => '=',
        path              => "/etc/keystone/keystone-paste.ini",
        subsetting        => "ec2_extension",
        value             => " voms",
        require           => Ini_setting["VOMS_filter"],
        notify            => Exec["reload"]
}

# keystone.conf
$defaults = { "path" => "/etc/keystone/keystone.conf" }
$voms_conf  = {
    "voms" => {
        "vomsdir_path"     => "/etc/grid-security/vomsdir",
        "ca_path"          => "/etc/grid-security/certificates",
        "voms_policy"      => "/etc/keystone/voms.json",
        "vomsapi_lib"      => "libvomsapi.so.1",
        "autocreate_users" => "True",
        "add_roles"        => "True",
        "user_roles"       => "_member_",
    }
}
create_ini_settings($voms_conf, $defaults)

# OPENSSL_ALLOW_PROXY_CERTS
if $::osfamily == "Debian" {
    file {
        "/etc/apache2/envvars":
            ensure  => present,
    }

    file_line {
        "apache_proxy_envvar":
            path    => "/etc/apache2/envvars",
            line    => "export OPENSSL_ALLOW_PROXY_CERTS=1",
            require => File["/etc/apache2/envvars"],
    }
}
elsif $::osfamily == "RedHat" {
    $apache_dir = "/etc/httpd"
    augeas {
        "Allow proxy certs":
            context => "/files/etc/sysconfig/httpd",
            changes => [
                "set OPENSSL_ALLOW_PROXY_CERTS 1",
            ],
    }

}

# Tenants/VOs
#define create_tenant {
#    # FIXME(orviz) Nova credentials hardcoded to /root/.nova/admin-novarc!
#    exec {
#        "Create project ${name}":
#            #command => "/bin/bash -c 'source /root/.nova/admin-novarc && openstack project create --domain default --enable ${name} --or-show'",
#            #command => "/bin/bash -c 'source /root/.nova/admin-novarc ; openstack --os-project-name \$OS_PROJECT_NAME --os-password \$OS_PASSWORD --os-username \$OS_USERNAME --os-auth-url \$OS_AUTH_URL --os-cacert \$OS_CACERT endpoint list'",
#            command => "openstack --os-password soplao10000 --os-username admin --os-project-name admin --os-auth-url https://${::fqdn}:5000/v2.0 --os-cacert /etc/grid-security/certificates/0d2a3bdd.0 endpoint list",
#            provider => shell,
#            path    => ["/usr/local/bin", "/usr/bin"],
#            logoutput => true
#    }
#}
#create_tenant { ["VO:dteam", "VO:ops.vo.ibergrid.eu"]: }
#keystone_tenant { ["VO:dteam", "VO:ops.vo.ibergrid.eu"]:
#  ensure  => present,
#  enabled => true,
#}

$voms_json_conf = '{
    "dteam": {
        "tenant": "VO:dteam"
    },
    "ops.vo.ibergrid.eu": {
        "tenant": "VO:ops.vo.ibergrid.eu"
    }
}'
file {
    "/etc/keystone/voms.json":
        ensure  => file,
        content => $voms_json_conf,
        owner   => "keystone",
        group   => "keystone",
        mode    => "0640",
        notify  => Exec["reload"]
}

voms::client{
    "dteam":
        vo => "dteam",
        servers => [{
            server => "voms.hellasgrid.gr",
            port   => "15004",
            dn     => "/C=GR/O=HellasGrid/OU=hellasgrid.gr/CN=voms.hellasgrid.gr",
            ca_dn  => "/C=GR/O=HellasGrid/OU=Certification Authorities/CN=HellasGrid CA 2016"
        },{
            server => "voms2.hellasgrid.gr",
            port   => "15004",
            dn     => "/C=GR/O=HellasGrid/OU=hellasgrid.gr/CN=voms2.hellasgrid.gr",
            ca_dn  => "/C=GR/O=HellasGrid/OU=Certification Authorities/CN=HellasGrid CA 2016"

        }],
        require => Class["Umd"]
}

voms::client{
    "ops.vo.ibergrid.eu":
        vo => "ops.vo.ibergrid.eu",
        servers => [{
            server => "voms01.ncg.ingrid.pt",
            port   => "15004",
            dn     => "/C=PT/O=LIPCA/O=LIP/OU=Lisboa/CN=voms01.ncg.ingrid.pt",
            ca_dn  => "/C=PT/O=LIPCA/CN=LIP Certification Authority"
        },{
            server => "ibergrid-voms.ifca.es",
            port   => "15004",
            dn     => "/DC=es/DC=irisgrid/O=ifca/CN=host/ibergrid-voms.ifca.es",
            ca_dn  => "/DC=es/DC=irisgrid/CN=IRISGridCA"
        }],
        require => Package["ca-policy-egi-core"]
}


## Misc

package {
    "fetch-crl":
        ensure => latest,
#        require => Package["ca-policy-egi-core"]
}

exec {
    "Execute fetch-crl":
        command => "/usr/sbin/fetch-crl -q && exit 0",
        require => Package["fetch-crl"]
}

#cron {
#    "fetch-crl":
#        command => "/usr/sbin/fetch-crl",
#        user    => "root",
#        minute  => "12",
#        hour    => [6,12,18,0],
#        weekday => "*",
#        require => Package["fetch-crl"],
#}

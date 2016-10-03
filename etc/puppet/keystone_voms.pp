## Base Keystone

Exec { logoutput => 'on_failure' }

if $::osfamily == 'Debian' {
    $pkgname = 'mariadb-client'
}
else {
    $pkgname = 'mariadb'
}

class { '::mysql::client':
    package_name => $pkgname,
}

class { '::mysql::server':
    package_name => 'mariadb-server',
    root_password           => 'TESTOWY',
    remove_default_accounts => true,
}
class { 'keystone::db::mysql':
    password      => 'super_secret_db_password',
    allowed_hosts => '%',
    #mysql_module  => '2.2',
}
class { 'keystone':
    verbose             => true,
    debug               => true,
    database_connection => 'mysql://keystone:super_secret_db_password@localhost/keystone',
    catalog_type        => 'sql',
    admin_token         => 'random_uuid',
    enabled             => false,
    enable_ssl          => true,
    #mysql_module        => '2.2',
    public_endpoint     => "https://${::fqdn}:5000/",
    admin_endpoint      => "https://${::fqdn}:35357/",
}

class { 'keystone::endpoint':
  public_url => "https://${::fqdn}:5000/",
  admin_url  => "https://${::fqdn}:35357/",
}


class { 'keystone::roles::admin':
    email    => 'test@puppetlabs.com',
    password => 'ChangeMe',
}

## WSGI Keystone

include apache
class { 'keystone::wsgi::apache':
    ssl               => true,
    ssl_cert          => "/etc/grid-security/hostcert.pem",
    ssl_key           => "/etc/grid-security/hostkey.pem",
    ssl_certs_dir     => "/etc/grid-security/certificates",
    ssl_crl_path      => "/etc/grid-security/certificates",
    ssl_verify_client => "optional",
    ssl_verify_depth  => "10",
    ssl_options       => "+StdEnvVars +ExportCertData",
}

#keystone_config { 'ssl/enable': value => true }

## Keystone VOMS ##

# keystone-paste.ini
keystone_paste_ini {
    "VOMS_filter":
        name      => "filter:voms/paste.filter_factory",
        value     => "keystone_voms.core:VomsAuthNMiddleware.factory",
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
        require           => Keystone_paste_ini["VOMS_filter"],
        notify            => Class['Apache::Service']
}

# keystone.conf
$defaults = { "path" => "/etc/keystone/keystone.conf" }
$voms_conf  = {
    "voms" => {
        "vomsdir_path" => "/etc/grid-security/vomsdir",
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
            require => Class["Keystone::Wsgi::Apache"]
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
keystone_tenant {
    "VO:dteam":
        ensure  => present,
        enabled => True,
}
keystone_tenant {
    "VO:ops.vo.ibergrid.eu":
        ensure  => present,
        enabled => True,
}

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
        notify  => Class['Apache::Service']
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

        }]
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
        }]
}


## Misc

package {
    "fetch-crl":
        ensure => latest,
}

cron {
    "fetch-crl":
        command => "/usr/sbin/fetch-crl",
        user    => "root",
        minute  => "12",
        hour    => [6,12,18,0],
        weekday => "*",
        require => Package["fetch-crl"],
}

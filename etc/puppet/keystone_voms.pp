Exec { logoutput => 'on_failure' }

class { 'mysql::server': }
class { 'keystone::db::mysql':
  #password => 'keystone',
    password      => 'super_secret_db_password',
    allowed_hosts => '%',
    mysql_module  => '2.2',
}
class { 'keystone':
    verbose        => true,
    debug          => true,
    sql_connection => 'mysql://keystone:super_secret_db_password@localhost/keystone',
    catalog_type   => 'sql',
    admin_token    => 'random_uuid',
    enabled        => false,
    enable_ssl     => true,
    mysql_module   => '2.2',
}
class { 'keystone::roles::admin':
  email    => 'test@puppetlabs.com',
  password => 'ChangeMe',
}
class { 'keystone::endpoint':
  public_url => "https://${::fqdn}:5000/",
  admin_url  => "https://${::fqdn}:35357/",
}

#keystone_config { 'ssl/enable': value => true }

include apache
class { 'keystone::wsgi::apache':
  ssl => true
}


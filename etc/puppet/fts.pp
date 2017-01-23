#Class['umd'] -> Class['fts::install'] -> Class['fts_mysql'] -> Class['fts::config'] -> Class['fts::service']

include umd
class {'fts::install': require => Class["umd"]}
class {'fts_mysql': require => Class["fts::install"]}
class {'fts::config': require => Class["fts_mysql"]}
class {'fts::service': require => Class["fts::config"]}


class fts_mysql {
    # FIXME(orviz) use mysql module for these execs
    $db_name = hiera("fts3_db_name")
    $db_user = hiera("fts3_db_username")
    $db_pass = hiera("fts3_db_password")
    $schema  = hiera("fts_schema", "/usr/share/fts-mysql/fts-schema-1.0.0.sql")

    if $::osfamily in ["Debian"] {
        $pkg = ["mysql-server", "mod_ssl"]
        $srv = "mysql"
    }
    elsif $::osfamily in ["RedHat", "CentOS"] {
        $pkg = ["mariadb-server", "mod_ssl"]
        $srv = "mariadb"
    }
    
    package {
        $pkg:
            ensure => installed,
    }
    
    service {
        $srv:
            enable  => true,
            ensure  => running,
            require => Package[$pkg],
    }

    exec {
        "drop-db-if-exists":
            command => "/usr/bin/mysql -e \"drop database IF EXISTS ftsdb\"",
            require => Service[$srv]
    }
    exec {
        "create-db":
            command => "/usr/bin/mysql -e \"create database ${db_name}\"",
            require => Exec["drop-db-if-exists"]
    }
    exec {
        "import-db":
            command => "/usr/bin/mysql ftsdb < $schema",
            require => Exec["create-db"]
    }
    exec {
        "grant-perms":
            command => "/usr/bin/mysql -e \"GRANT ALL ON ${db_name}.* TO ${db_user}@'localhost' IDENTIFIED BY '${db_pass}';\"",
            require => Exec["import-db"]
    }
    exec {
        "flush-privileges":
            command => "/usr/bin/mysql -e \"FLUSH PRIVILEGES;\"",
            require => Exec["grant-perms"]
    }
}
#class {
#    "fts":
#        require => [Class["umd"], Exec["flush-privileges"]]
#}


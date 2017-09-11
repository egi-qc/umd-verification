class ooi_start {
    $systemd_occi_str = "

[Unit]
Description = Devstack devstack@n-api-occi.service

[Service]
RestartForceExitStatus = 100
NotifyAccess = all
Restart = always
KillSignal = SIGQUIT
Type = notify
ExecStart = /usr/bin/uwsgi --procname-prefix nova-api-occi --ini /etc/nova/nova-api-occi-uwsgi.ini
User = stack
SyslogIdentifier = devstack@n-api-occi.service

[Install]
WantedBy = multi-user.target
    "
    $uwsgi_init_str = "

[uwsgi]
http = :8787
lazy-apps = true
add-header = Connection: close
buffer-size = 65535
thunder-lock = true
plugins = python
enable-threads = true
exit-on-reload = true
die-on-term = true
master = true
processes = 2
wsgi-file = /usr/bin/nova-api-wsgi
    "

    exec {
        "Enable ooi API":
            command => "/bin/sed -i '/enabled_apis*/c\enabled_apis = osapi_compute,metadata,ooi' /etc/nova/nova.conf",
            require => Class["ooi"]
    }
 
    file {
        "/etc/nova/nova-api-occi-uwsgi.ini":
            content => $uwsgi_init_str
    }
 
    file {
        "/etc/systemd/system/devstack\@n-api-occi.service":
            content => $systemd_occi_str,
            require => File["/etc/nova/nova-api-occi-uwsgi.ini"],
            notify  => Exec["reload systemctl"]
    }

    exec {
        "reload systemctl":
            command   => "/bin/systemctl daemon-reload",
            subscribe => File["/etc/systemd/system/devstack\@n-api-occi.service"]
    }

    exec {
        "start devstack\@n-api-occi.service":
            command => "/bin/systemctl restart "devstack@n-api-occi*",
            require => Exec["reload systemctl"]
    }
}

include umd
class {
    "ooi":
        manage_repos   => false,
        manage_service => false,
        require        => Class["umd"]
}
class {"ooi_start": require => Class["ooi"]}

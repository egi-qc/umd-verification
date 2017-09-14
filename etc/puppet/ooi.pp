class ooi_start {
    if $::osfamily == "RedHat" {
        $bin_path = "/usr/bin"
    }
    else {
        $bin_path = "/usr/local/bin"
    }
    $systemd_occi_str = "

[Unit]
Description = Devstack devstack@n-api-occi.service

[Service]
RestartForceExitStatus = 100
NotifyAccess = all
Restart = always
KillSignal = SIGQUIT
Type = notify
ExecStart = ${bin_path}/uwsgi --procname-prefix nova-api-occi --ini /etc/nova/nova-api-occi-uwsgi.ini
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
wsgi-file = /usr/bin/nova-api-occi-wsgi
    "

    $wsgi_app_str = "
from nova.api.openstack import wsgi_app

NAME = \"ooi\"


def init_application():
    return wsgi_app.init_application(NAME)
    "

    $wgsi_nova_str = "
#!/usr/bin/python
import threading
from nova.api.openstack.compute.wsgi_occi import init_application
application = None
app_lock = threading.Lock()

with app_lock:
    if application is None:
        application = init_application()
    "

    exec {
        "Enable ooi API":
            command => "/bin/sed -i '/enabled_apis*/c\enabled_apis = osapi_compute,metadata,ooi' /etc/nova/nova.conf",
            require => Class["ooi"]
    }
 
    file {
        "/etc/nova/nova-api-occi-uwsgi.ini":
            content => $uwsgi_init_str,
            owner   => "stack",
            group   => "stack"
    }

    file {
        "/opt/stack/nova/nova/api/openstack/compute/wsgi_occi.py":
            content => $wsgi_app_str,
            owner   => "stack",
            group   => "stack",
            mode    => "0644",
            require => File["/etc/nova/nova-api-occi-uwsgi.ini"]
    }

    file {
        "/usr/bin/nova-api-occi-wsgi":
            content => $wgsi_nova_str,
            owner   => "root",
            group   => "root",
            mode    => "0755",
            require => File["/opt/stack/nova/nova/api/openstack/compute/wsgi_occi.py"]
    }
 
    file {
        "/etc/systemd/system/devstack@n-api-occi.service":
            content => $systemd_occi_str,
            require => File["/etc/nova/nova-api-occi-uwsgi.ini"],
            notify  => Exec["reload systemctl"]
    }

    exec {
        "reload systemctl":
            command   => "/bin/systemctl daemon-reload",
            subscribe => File["/etc/systemd/system/devstack@n-api-occi.service"]
    }

    exec {
        "start devstack@n-api-occi.service":
            command => "/bin/systemctl restart devstack@n-api-occi",
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

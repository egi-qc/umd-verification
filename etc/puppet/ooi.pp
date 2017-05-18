include umd

class {
    "ooi":
        manage_repos      => false,
        manage_service    => false,
        require           => Class["umd"],
}

exec {
    "Enable ooi API":
        command => "/bin/sed -i '/enabled_apis*/c\enabled_apis = osapi_compute,metadata,ooi' /etc/nova/nova.conf",
        require => Class["ooi"]
}

exec {
    "kill nova-api":
        command => "pkill -9 -f nova-api",
        path    => ["/usr/bin", "/usr/local/bin"],
        onlyif  => "pgrep -fc nova-api",
        require => Exec["Enable ooi API"]
}

exec {
    "Start nova-api":
        command  => "/usr/local/bin/nova-api & echo $! >/opt/stack/status/stack/n-api.pid; fg || echo \"n-api failed to start\" | tee \"/opt/stack/status/stack/n-api.failure\"",
        user     => "stack",
        provider => shell,
        path     => ["/usr/bin", "/usr/local/bin"],
        require  => Exec["kill nova-api"]
}

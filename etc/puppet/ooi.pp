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
    "Restart nova-api in devstack":
        command => "pkill -9 -f nova-api && nohup python nova-api &",
        path    => ["/usr/bin", "/usr/local/bin"],
        require => Exec["Enable ooi API"]
}

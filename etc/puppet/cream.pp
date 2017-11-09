class {"umd": before => [Class["gridftp::install"], Class["creamce::install"]]}

class {
    "creamce":
        require => [
            Class["umd"],
        ]
}

class slurmmaster::install {
    if $::osfamily == "RedHat" {
        $pkgs = {
            "slurm-plugins" => { source => "https://depot.galaxyproject.org/yum/el/7/x86_64/slurm-plugins-17.02.6-1.el7.centos.x86_64.rpm",
                                 name   => "slurm-plugins", },
            "slurm"         => { source => "https://depot.galaxyproject.org/yum/el/7/x86_64/slurm-17.02.6-1.el7.centos.x86_64.rpm",
                                 name   => "slurm", },
            "slurm-munge"   => { source => "https://depot.galaxyproject.org/yum/el/7/x86_64/slurm-munge-17.02.6-1.el7.centos.x86_64.rpm",
                                 name   => "slurm-munge", },

        }
        create_resources(package, $pkgs)
    }
}
include slurmmaster::install

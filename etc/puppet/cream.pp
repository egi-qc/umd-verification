class {"umd": before => [Class["gridftp::install"], Class["creamce::install"]]}

class {
    "creamce":
        require => [
            Class["umd"],
        ]
}

include slurm

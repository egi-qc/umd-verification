class {"umd": before => [Class["gridftp::install"], Class["creamce::install"]]}

## Uncomment for torque deployment
#$torque_pkgs = [
#    "torque-client",
#    "torque-server"
#]
#package {
#    $torque_pkgs:
#        ensure => present
#}
#
#$wns = {'host1' => { ip => '172.16.39.154'}}
#create_resources(host, $wns)

class {
    "creamce":
        require => [
            Class["umd"],
        ]
}

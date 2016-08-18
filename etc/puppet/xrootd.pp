#include gridftp::params
#file { $xrootd::params::certificate: }
#file { $xrootd::params::key: }
file { "/etc/grid-security/hostcert.pem": }
file { "/etc/grid-security/hostkey.pem": }

include xrootd

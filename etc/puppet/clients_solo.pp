include umd

$clients = [
    "CGSI-gSOAP",
    "davix",
    "davix-libs",
    "gfal2",
    "gfal2-python",
    "gfal2-util",
    "gfal2-plugin-srm",
    "gfal2-plugin-lfc",
    "gfal2-plugin-http",
    "gfal2-plugin-rfio",
    "gfal2-plugin-gridftp",
    "gfal2-plugin-xrootd",
    "gfal2-plugin-file",
    "gfal2-plugin-dcap",
    "gfalFS",
    "myproxy",
    "srm-ifce",
    "voms-clients-cpp",
    "voms-clients-java",
]

package {
    $clients:
	ensure  => latest,
        require => Class["umd"]
}

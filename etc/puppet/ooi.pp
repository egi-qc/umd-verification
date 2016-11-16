include umd

class {
    "ooi":
        openstack_version => "mitaka",
        manage_repos      => false,
        manage_services   => false,
        require           => Class["umd"],
}

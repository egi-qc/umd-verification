include umd

class {
    "ooi":
        openstack_version => "mitaka",
        manage_repos      => false,
        manage_service    => false,
        require           => Class["umd"],
}

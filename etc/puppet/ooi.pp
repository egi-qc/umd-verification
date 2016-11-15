include umd

class {
    "ooi":
        openstack_version => "mitaka",
        require           => Class["umd"],
}

include umd

class {
    "ooi":
        manage_repos      => false,
        manage_service    => false,
        require           => Class["umd"],
}

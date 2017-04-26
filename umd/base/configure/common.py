from umd import config
from umd import utils as base_utils


def set_umd_params(template_file, output_file):
    _distribution = config.CFG["distribution"]
    if _distribution == "umd":
        _release = "umd_release"
    elif _distribution == "cmd":
        _release = "cmd_release"

    _data = {
        "release": config.CFG[_release],
        "distribution": _distribution,
        "repository_file": config.CFG.get("repository_file", ""),
        "openstack_release": config.CFG.get("openstack_release", ""),
        "igtf_repo": "undef",
    }
    
    if config.CFG.get("need_cert", ""):
        _data["igtf_repo"] = "yes",

    base_utils.render_jinja(
        template_file,
        _data,
        output_file=output_file)

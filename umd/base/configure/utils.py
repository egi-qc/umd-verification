from umd import config
from umd import utils as base_utils


def set_runtime_params(template_file, output_file):
    _distribution = config.CFG["distribution"]
    if _distribution == "umd":
        _release = "umd_release"
    elif _distribution == "cmd":
        _release = "cmd_release"
    if config.CFG.get("need_cert", ""):
        _igtf_repo = "true"
    else:
        _igtf_repo = "false"
    _data = {
        "release": config.CFG[_release],
        "distribution": _distribution,
        "repository_file": config.CFG.get("repository_file", ""),
        "openstack_release": config.CFG.get("openstack_release", ""),
        "igtf_repo": _igtf_repo,
    }
    base_utils.render_jinja(
        template_file,
        _data,
        output_file=os.path.join(self.hiera_data_dir, output_file))

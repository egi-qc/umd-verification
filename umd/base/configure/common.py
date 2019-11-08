# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from umd import config
from umd import utils as base_utils


def set_umd_params(template_file, output_file):
    _distribution = config.CFG["distribution"]
    _data = {
        "distribution": _distribution,
        "repository_file": config.CFG.get("repository_file", ""),
        "igtf_repo": "False",
        "enable_testing_repo": config.CFG.get("enable_testing_repo", "False"),
        "enable_untested_repo": config.CFG.get("enable_untested_repo",
                                               "False"),
    }

    if _distribution == "umd":
        _release = config.CFG["umd_release"]
    elif _distribution == "cmd":
        _release = config.CFG["cmd_release"]
        if config.CFG.get("openstack_release", False):
            _data["openstack_release"] = config.CFG["openstack_release"]
    elif _distribution == "cmd-one":
        _release = config.CFG["cmd_one_release"]
    _data["release"] = _release

    # if config.CFG.get("need_cert", ""):
    #     _data["igtf_repo"] = "True"
    base_utils.render_jinja(
        template_file,
        _data,
        output_file=output_file)

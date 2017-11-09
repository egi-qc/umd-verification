import collections
import os.path

import yaml

from umd import api
from umd import system


class DefaultsDict(collections.defaultdict):
    def __getitem__(self, item):
        v = collections.defaultdict.__getitem__(self, item)
        if isinstance(v, dict):
            return collections.defaultdict(str, v)
        else:
            return v


class ConfigDict(dict):
    def __init__(self):
        self.defaults = DefaultsDict(lambda: collections.defaultdict(str),
                                     self.load_defaults())

    def load_defaults(self):
        with open("etc/defaults.yaml", "rb") as f:
            return yaml.safe_load(f)

    def set_defaults(self):
        self.__setitem__("log_path", self.defaults["base"]["log_path"])
        self.__setitem__("jinja_template_dir",
                         self.defaults["base"]["jinja_template_dir"])
        self.__setitem__("yaim_path", self.defaults["yaim"]["path"])
        self.__setitem__("puppet_path", self.defaults["puppet"]["path"])
        self.__setitem__("umdnsu_url", self.defaults["nagios"]["umdnsu_url"])
        self.__setitem__(
            "puppet_release",
            self.defaults["puppet_release"][system.distro_version])

    def validate(self):
        # Strong validations first: (umd_release, repository_url)
        v_umd_release = self.get("umd_release", None)
        v_cmd_release = self.get("cmd_release", None)
        v_repo = self.get("repository_url", None)
        v_repo_file = self.get("repository_file", None)
        if not v_umd_release and not v_cmd_release:
            if self.get("cmd_one_release", None):
                v_cmd_release = self.get("cmd_one_release")
            else:
                api.fail(("No UMD or CMD release was selected: cannot start "
                          "deployment"), stop_on_error=True)
        else:
            api.info("Using UMD %s release repository" % v_umd_release)

        if v_repo:
            api.info("Using UMD verification repository: %s" % v_repo)

        if v_repo_file:
            api.info("Using UMD verification repository file: %s"
                     % v_repo_file)

        # Configuration management: Puppet
        from umd.base.configure.puppet import PuppetConfig
        if isinstance(self.__getitem__("cfgtool"), PuppetConfig):
            if not self.__getitem__("puppet_release"):
                api.fail(("No Puppet release package defined for '%s' "
                          "distribution" % system.distname),
                         stop_on_error=True)

    def update(self, d):
        d_tmp = {}
        for k, v in d.items():
            if v:
                append_arg = False
                # Special treatments
                if k.startswith("repository_url"):
                    item = "repository_url"
                    append_arg = True
                elif k.startswith("repository_file"):
                    item = "repository_file"
                    append_arg = True
                elif k.startswith("qc_step"):
                    item = "qc_step"
                    append_arg = True
                elif k.startswith("umd_release"):
                    if not self.get("umd_release_pkg", None):
                        pkg = self.defaults[(
                            "umd_release")][int(v)][system.distro_version]
                        d_tmp["umd_release_pkg"] = pkg
                    # set 'distribution'
                    d_tmp["distribution"] = "umd"
                elif k.startswith("cmd_one_release"):
                    # set 'distribution'
                    d_tmp["distribution"] = "cmd-one"
                elif k.startswith("cmd_release"):
                    # set 'distribution'
                    d_tmp["distribution"] = "cmd"
                elif k.startswith("package"):
                    item = "metapkg"
                    append_arg = True
                elif k.startswith("func_id"):
                    item = "qc_specific_id"
                    append_arg = True
                elif k.startswith("log_path"):
                    if not os.path.isabs(v):
                        v = os.path.join(os.getcwd(), v)

                # Parameters that accept lists
                if append_arg:
                    try:
                        l = d_tmp[item]
                    except KeyError:
                        l = []
                    if l:
                        if v not in l:
                            l.append(v)
                            d_tmp[item] = l
                    else:
                        if isinstance(v, list):
                            d_tmp[item] = v
                        else:
                            d_tmp[item] = [v]
                else:
                    d_tmp[k] = v
            else:
                d_tmp[k] = v

        super(ConfigDict, self).update(d_tmp)

CFG = ConfigDict()


def cfg_item(i):
    try:
        return CFG[i]
    except KeyError:
        return None

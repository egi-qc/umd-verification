import yaml

from umd import system


def load_defaults():
    with open("etc/defaults.yaml", "rb") as f:
        return yaml.safe_load(f)


class ConfigDict(dict):
    def __init__(self):
        DEFAULTS = load_defaults()
        self.__setitem__("repository_url", "")
        self.__setitem__("epel_release", DEFAULTS["epel_release"][system.distro_version])
        self.__setitem__("umd_release", DEFAULTS["umd_release"][system.distro_version])
        self.__setitem__("igtf_repo", DEFAULTS["igtf_repo"][system.distname])
        self.__setitem__("yaim_path", DEFAULTS["yaim"]["path"])
        self.__setitem__("log_path", DEFAULTS["base"]["log_path"])

    #def __setitem__(self, k, v):
    #    if v:
    #        return super(ConfigDict, self).__setitem__(k, v)

    def update(self, d):
        for k, v in d.items():
            append_arg = False
            if k.startswith("repository_url"):
                item = "repository_url"
                append_arg = True
            elif k.startswith("qc_step"):
                item = "qc_step"
                append_arg = True

            if append_arg:
                try:
                    l = self.__getitem__(item)
                except KeyError:
                    l = []
                if l:
                    self.__setitem__(item, l.append(v))
                else:
                    self.__setitem__(item, [v])
            else:
                self.__setitem__(k, v)

CFG = ConfigDict()

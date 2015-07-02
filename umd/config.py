import yaml

from umd import system


def load_defaults():
    with open("etc/defaults.yaml", "rb") as f:
        return yaml.safe_load(f)


class ConfigDict(dict):
    def __init__(self):
        DEFAULTS = load_defaults()
        self.__setitem__("repository_url", "")
        self.__setitem__("umd_release", DEFAULTS["umd_release"][system.distro_version])
        self.__setitem__("igtf_repo", DEFAULTS["igtf_repo"][system.distname])
        self.__setitem__("yaim_path", DEFAULTS["yaim"]["path"])
        self.__setitem__("log_path", DEFAULTS["base"]["log_path"])
        if system.distname == "redhat":
            self.__setitem__("epel_release", DEFAULTS["epel_release"][system.distro_version])

    def update(self, d):
        d_tmp = {}
        for k, v in d.items():
            if v:
                append_arg = False
                if k.startswith("repository_url"):
                    item = "repository_url"
                    append_arg = True
                elif k.startswith("qc_step"):
                    item = "qc_step"
                    append_arg = True

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
                        d_tmp[item] = [v]
                else:
                    d_tmp[k] = v
            else:
                d_tmp[k] = v

        super(ConfigDict, self).update(d_tmp)


CFG = ConfigDict()

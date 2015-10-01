import yaml

from umd import api
from umd import system


def load_defaults():
    with open("etc/defaults.yaml", "rb") as f:
        return yaml.safe_load(f)


class ConfigDict(dict):
    def __init__(self):
        self.defaults = load_defaults()

    def validate(self):
        try:
            self.defaults["umd_release"][system.distro_version]
            self.defaults["igtf_repo"][system.distname]
        except KeyError:
            api.info("'%s' OS not supported" % system.distro_version)

    def set(self):
        self.__setitem__("repository_url", "")
        self.__setitem__(
            "umd_release",
            self.defaults["umd_release"][system.distro_version])
        # Configuration management
        self.__setitem__(
            "puppet_release",
            self.defaults["puppet_release"][system.distro_version])
        # IGTF
        self.__setitem__(
            "igtf_repo",
            self.defaults["igtf_repo"][system.distname])
        if "igtf_repo_key" in self.defaults.keys():
            self.__setitem__(
                "igtf_repo_key",
                self.defaults["igtf_repo_key"][system.distname])
        self.__setitem__("yaim_path", self.defaults["yaim"]["path"])
        self.__setitem__("puppet_path", self.defaults["puppet"]["path"])
        self.__setitem__("log_path", self.defaults["base"]["log_path"])
        self.__setitem__("umdnsu_url", self.defaults["nagios"]["umdnsu_url"])
        if system.distname in ["redhat", "centos"]:
            self.__setitem__(
                "epel_release",
                self.defaults["epel_release"][system.distro_version])

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

import yaml

from umd import system


def load_defaults():
    with open("etc/defaults.yaml", "rb") as f:
        return yaml.safe_load(f)


class ConfigDict(dict):
    def __setitem__(self, k, v):
        if v:
            return super(ConfigDict, self).__setitem__(k, v)

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


DEFAULTS = load_defaults()
CFG = ConfigDict({
    "repository_url": "",
    "epel_release": DEFAULTS["epel_release"][system.distro_version],
    "umd_release": DEFAULTS["umd_release"][system.distro_version],
    "igtf_repo": DEFAULTS["igtf_repo"][system.distname],
    "yaim_path": DEFAULTS["yaim"]["path"],
    "log_path": DEFAULTS["base"]["log_path"]})

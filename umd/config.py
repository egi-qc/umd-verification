import collections

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
        self.__setitem__("yaim_path", self.defaults["yaim"]["path"])
        self.__setitem__("puppet_path", self.defaults["puppet"]["path"])
        self.__setitem__("log_path", self.defaults["base"]["log_path"])
        self.__setitem__("umdnsu_url", self.defaults["nagios"]["umdnsu_url"])
        self.__setitem__(
            "umd_release",
            self.defaults["umd_release"][system.distro_version])
        self.__setitem__(
            "igtf_repo",
            self.defaults["igtf_repo"][system.distname])
        self.__setitem__(
            "igtf_repo_key",
            self.defaults["igtf_repo_key"][system.distname])
        self.__setitem__(
            "puppet_release",
            self.defaults["puppet_release"][system.distro_version])
        self.__setitem__(
            "epel_release",
            self.defaults["epel_release"][system.distro_version])

    def validate(self):
        # Strong validations first
        # UMD release
        if not self.__getitem__("umd_release"):
            # FIXME(orviz) centos7 does not have UMD release package
            if system.distname not in ["centos"]:
                api.fail(("UMD release package not provided for '%s' "
                          "distribution" % system.distname),
                         stop_on_error=True)
        # Configuration management: Puppet
        from umd.base.configure.puppet import PuppetConfig
        if isinstance(self.__getitem__("cfgtool"), PuppetConfig):
            if not self.__getitem__("puppet_release"):
                api.fail(("No Puppet release package defined for '%s' "
                          "distribution" % system.distname),
                         stop_on_error=True)
        # EPEL release
        if system.distname in ["centos", "redhat"]:
            if not self.__getitem__("epel_release"):
                api.fail(("EPEL release package not provided for '%s' "
                          "distribution" % system.distname),
                         stop_on_error=True)
        # Type of installation
        if not self.__getitem__("installation_type"):
            api.warn("No installation type provided: performing installation.")
            self.__setitem__("installation_type", "install")
        # Verification repository URL
        v = self.__getitem__("repository_url")
        if not v:
            api.warn("No verification repository URL provided.")
        # Metapackage
        v = self.__getitem__("metapkg")
        if v:
            msg = "Metapackage/s selected: %s" % ''.join([
                "\n\t+ %s" % mpkg for mpkg in v])
            api.info(msg)

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


from fabric.api import local
from fabric.colors import green,yellow
from fabric.context_managers import lcd,prefix

from tempfile import NamedTemporaryFile

from umd.base import utils as base_utils
from umd.base.configure import utils as conf_utils

class YaimConfig(object):
    def __init__(self, nodetype, siteinfo):
	self.nodetype = nodetype
	self.siteinfo = siteinfo

    def run(self, config_path):
        self.nodetype = base_utils.to_list(self.nodetype)
        self.siteinfo = base_utils.to_list(self.siteinfo)

        with NamedTemporaryFile("w+t", dir=config_path, delete=True) as f:
            if conf_utils.generate_cert(self.nodetype):
                print(yellow("Certificate issued for nodetype/s '%s'" % self.nodetype))

            for si in self.siteinfo:
                f.write("source %s\n" % si)
            f.flush()

            print(green("Creating temporary file '%s' with content:" % f.name))
            local("cat %s" % f.name)

            with lcd(config_path):
                with prefix("source %s" % f.name):
                    local("/opt/glite/yaim/bin/yaim -c -s %s -n %s"
                            % (f.name,
                               " -n ".join(self.nodetype)))

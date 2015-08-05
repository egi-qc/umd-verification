import tempfile

from fabric import api as fabric_api
from fabric import context_managers

from umd import api
from umd import config
from umd import exception
from umd import utils


class YaimConfig(object):
    def __init__(self, pre_config, post_config):
        self.nodetype = config.CFG["nodetype"]
        self.siteinfo = config.CFG["siteinfo"]
        self.config_path = config.CFG["yaim_path"]
        self.pre_config = pre_config
        self.post_config = post_config
        self.has_run = False

    def run(self):
        self.pre_config()

        self.nodetype = utils.to_list(self.nodetype)
        self.siteinfo = utils.to_list(self.siteinfo)

        if not self.nodetype or not self.siteinfo:
            raise exception.ConfigException(("Could not run YAIM: Bad "
                                             "nodetype or site-info."))

        with tempfile.NamedTemporaryFile("w+t",
                                         dir=self.config_path,
                                         delete=True) as f:
            for si in self.siteinfo:
                f.write("source %s\n" % si)
            f.flush()

            api.info(("Creating temporary file '%s' with "
                      "content: %s" % (f.name, f.readlines())))

            # NOTE(orviz) Cannot use 'capture=True': execution gets
            # stalled (defunct)
            with context_managers.lcd(self.config_path):
                abort_exception_default = fabric_api.env.abort_exception
                fabric_api.env.abort_exception = exception.ConfigException
                try:
                    fabric_api.local("/opt/glite/yaim/bin/yaim -c -s %s -n %s"
                                     % (f.name, " -n ".join(self.nodetype)))
                except exception.ConfigException:
                    fabric_api.abort(api.fail(("YAIM execution failed. Check "
                                               "the logs at '/opt/glite/yaim/"
                                               "log/yaimlog'.")))
                api.info("YAIM configuration ran successfully.")
                fabric_api.env.abort_exception = abort_exception_default

        self.post_config()
        self.has_run = True

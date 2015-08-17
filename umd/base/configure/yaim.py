import tempfile

from fabric import api as fabric_api
from fabric import context_managers

from umd import api
from umd.base.configure import BaseConfig
from umd import config
from umd import exception
from umd import utils


class YaimConfig(BaseConfig):
    def __init__(self,
                 nodetype,
                 siteinfo):
        """Runs YAIM configurations.

        :nodetype: YAIM nodetype to configure.
        :siteinfo: File containing YAIM configuration variables.
        """
        self.nodetype = nodetype
        self.siteinfo = siteinfo

    def config(self):
        self.nodetype = utils.to_list(self.nodetype)
        self.siteinfo = utils.to_list(self.siteinfo)

        if not self.nodetype or not self.siteinfo:
            raise exception.ConfigException(("Could not run YAIM: Bad "
                                             "nodetype or site-info."))

        with tempfile.NamedTemporaryFile("w+t",
                                         dir=config.CFG["yaim_path"],
                                         delete=True) as f:
            for si in self.siteinfo:
                f.write("source %s\n" % si)
            f.flush()

            api.info(("Creating temporary file '%s' with "
                      "content: %s" % (f.name, f.readlines())))

            # NOTE(orviz) Cannot use 'capture=True': execution gets
            # stalled (defunct)
            with context_managers.lcd(config.CFG["yaim_path"]):
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

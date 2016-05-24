import os
import subprocess
import tempfile

import mock

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

        # FIXME(orviz) Not using Fabric to run this command
        r = mock.MagicMock()
        r.failed = True

        with tempfile.NamedTemporaryFile("w+t",
                                         dir=config.CFG["yaim_path"],
                                         delete=True) as f:
            for si in self.siteinfo:
                f.write("source %s\n" % si)
            f.flush()

            api.info(("Creating temporary file '%s' with "
                      "content: %s" % (f.name, f.readlines())))

            dirlast = os.getcwd()
            os.chdir(config.CFG["yaim_path"])
            api.info("Running YAIM tool: %s" % ' '.join([
                "/opt/glite/yaim/bin/yaim",
                "-c",
                "-s",
                f.name,
                "-n",
                " -n ".join(self.nodetype)]))
            p = subprocess.Popen([
                "/opt/glite/yaim/bin/yaim",
                "-c",
                "-s",
                f.name,
                "-n",
                " -n ".join(self.nodetype)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE)
            p.communicate()
            os.chdir(dirlast)

            utils.runcmd("cp /opt/glite/yaim/log/yaimlog %s/"
                         % config.CFG["log_path"])

            if p.returncode:
                api.fail(("YAIM execution failed. Check "
                          "the logs at '/opt/glite/yaim/log/yaimlog'."))
            else:
                api.info("YAIM configuration ran successfully.")
                r.failed = False

        self.has_run = True

        return r

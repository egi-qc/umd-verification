from umd import api
from umd.base.configure import BaseConfig
from umd import utils


class ScriptConfig(BaseConfig):
    def __init__(self, script):
        """Simple script configurations.

        :script: Location of the script to be ran.
        """
        self.script = script

    def config(self, logfile=None):
        r = utils.runcmd(self.script, log_to_file=logfile)
        if r.failed:
            api.fail("Script configuration failed: %s"
                     % self.script, stop_on_error=True)

        self.has_run = True

        return r

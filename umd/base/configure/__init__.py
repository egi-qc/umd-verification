from umd import api
from umd import config
from umd import utils


EXTRA_VARS_FILE = "/tmp/extra_vars.yaml"


class BaseConfig(object):
    """Base class for all the configuration types."""
    def __init__(self, *args, **kwargs):
        self.has_run = False
        self.logfile = None
        self.extra_vars = None

    def _add_extra_vars(self, fname=None):
        """Method to add extra variables needed by the automation tool."""
        _fname = EXTRA_VARS_FILE
        if fname:
            _fname = fname
        if utils.to_yaml(_fname, self.extra_vars, destroy=True):
            api.info("Extra vars file added: %s" % _fname)

        return EXTRA_VARS_FILE

    def _extra_repo(self):
        """Method where testing/preview/.. repos are enabled."""
        if "enable_testing_repo" in config.CFG.keys():
            utils.enable_repo("UMD-testing",
                              local_repo=True,
                              name="UMD-*-testing")

    def _deploy(self):
        """Method where the client tool is deployed."""
        pass

    def pre_config(self):
        pass

    def config(self):
        raise NotImplementedError

    def post_config(self):
        pass

    def run(self):
        self._extra_repo()
        self._deploy()

        self.pre_config()
        r = self.config()
        self.post_config()

        if r.failed:
            api.fail("Configuration has failed.", stop_on_error=True)
        return r

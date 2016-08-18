from umd import api


class BaseConfig(object):
    """Base class for all the configuration types."""
    def __init__(self, *args, **kwargs):
        self.has_run = False
        self.logfile = None

    def pre_config(self):
        pass

    def config(self):
        raise NotImplementedError

    def post_config(self):
        pass

    def run(self):
        self.pre_config()
        r = self.config()
        self.post_config()

        if r.failed:
            api.fail("Configuration has failed.", stop_on_error=True)
        return r

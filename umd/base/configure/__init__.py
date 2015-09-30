class BaseConfig(object):
    """Base class for all the configuration types."""
    def init(self, *args, **kwargs):
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

        return r

import tempfile
from fabric.api import env
from fabric.api import local
from fabric.context_managers import lcd

from umd.api import fail
from umd.api import info
from umd import exception
from umd.utils import to_list


class YaimConfig(object):
    def __init__(self,
                 nodetype,
                 siteinfo,
                 config_path,
                 pre_config,
                 post_config):
        self.nodetype = nodetype
        self.siteinfo = siteinfo
        self.config_path = config_path
        self.pre_config = pre_config
        self.post_config = post_config
        self.has_run = False

    def run(self, qc_step):
        self.pre_config()

        self.nodetype = to_list(self.nodetype)
        self.siteinfo = to_list(self.siteinfo)

        if not self.nodetype or not self.siteinfo:
            raise exception.ConfigException(("Could not run YAIM: Bad "
                                             "nodetype or site-info."))

        with tempfile.NamedTemporaryFile("w+t",
                                         dir=self.config_path,
                                         delete=True) as f:
            for si in self.siteinfo:
                f.write("source %s\n" % si)
            f.flush()

            info(("Creating temporary file '%s' with "
                  "content: %s" % (f.name, f.readlines())))

            # NOTE(orviz) Cannot use 'capture=True': execution gets
            # stalled (defunct)
            with lcd(self.config_path):
                abort_exception_default = env.abort_exception
                env.abort_exception = exception.ConfigException
                try:
                    local("/opt/glite/yaim/bin/yaim -c -s %s -n %s"
                          % (f.name, " -n ".join(self.nodetype)))
                except exception.ConfigException:
                    fail(("YAIM execution failed. Check the logs at "
                          "'/opt/glite/yaim/log/yaimlog'."))
                info("YAIM configuration ran successfully.")
                env.abort_exception = abort_exception_default

        self.post_config()
        self.has_run = True

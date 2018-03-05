# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from umd import api
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
        self._deploy()

        self.pre_config()
        r = self.config()
        self.post_config()

        if r.failed:
            api.fail("Configuration has failed.", stop_on_error=True)
        return r

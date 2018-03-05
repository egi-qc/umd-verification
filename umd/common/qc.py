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

import functools

from fabric import colors

from umd import api
from umd import config
from umd import utils


def qcstep_request(f):
    """Decorator method that handles on-demand QC step executions."""
    def _request(self, *args, **kwargs):
        step_methods = []
        if "qc_step" in kwargs.keys():
            for step in utils.to_list(kwargs["qc_step"]):
                try:
                    method = getattr(self, step.lower())
                    step_methods.append(method)
                except AttributeError:
                    api.info("Ignoring QC step '%s': not defined." % step)
                    continue
        return f(self, step_methods, *args, **kwargs)
    return _request


def qcstep(id, description):
    """Decorator method that prints QC step header."""
    def _qcstep(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            print("[[%s: %s]]" % (colors.blue(id),
                                  colors.blue(description)))
            return f(*args, **kwargs)
        return wrapper
    return _qcstep


def get_qc_envvars():
    """Returns a dict with the bash environment variables found in conf."""
    return dict([(k.split("qcenv_")[1], v)
                 for k, v in config.CFG.items() if k.startswith("qcenv")])

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

from fabric import api as fabric_api
from fabric import colors


def _format_error_msg(logs, cmd=None):
    msg_l = []
    if logs:
        msg_l.append("See more information in logs (%s)." % ','.join(logs))
    if cmd:
        msg_l.append("Error while executing command '%s'." % cmd)

    return ' '.join(msg_l)


def format(f):
    """Decorator class to append stderr/stdout log locations."""
    def _format(*args, **kwargs):
        args = list(args)
        msg = args.pop()
        logfile = kwargs.pop("logfile", None)
        if logfile:
            msg = ' '.join([msg, _format_error_msg(logfile)])
        return f(msg, *args, **kwargs)
    return _format


def info(msg):
    """Prints info/debug logs."""
    fabric_api.puts("[INFO] %s" % msg)


@format
def fail(msg, stop_on_error=False):
    """Prints fail messages."""
    msg = "[%s] %s" % (colors.red("FAIL"), msg)
    if stop_on_error:
        fabric_api.abort(fabric_api.puts(msg))
    else:
        fabric_api.puts(msg)


def ok(msg):
    """Prints ok messages."""
    fabric_api.puts("[OK] %s" % msg)


@format
def warn(msg):
    """Prints warn messages."""
    fabric_api.puts("[%s] %s" % (colors.yellow("WARN"), msg))


def na(msg):
    """Prints NA messages."""
    fabric_api.puts("[%s] %s" % (colors.yellow("NA"), msg))

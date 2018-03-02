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

import collections
import os
import pwd

import yaml

from umd import api
from umd.common import qc
from umd import config
from umd import utils


# FIXME Move to defaults.yaml
QC_SPECIFIC_FILE = "etc/qc_specific.yaml"


class Validate(object):
    def _is_executable(self, f):
        """File executable check."""
        is_executable = False
        if os.access(f, os.X_OK):
            is_executable = True

        return is_executable

    def _get_files_from_dir(self, dir):
        """Returns the list of files contained within a given directory."""
        l = []
        for root, dirs, files in os.walk(dir):
            for f in files:
                l.append(os.path.join(root, f))
        return l

    def _handle_user(self, user, logfile):
        """Assures that the given user exists (creates it if needed)."""
        try:
            pwd.getpwnam(user)
        except KeyError:
            if user:
                utils.runcmd("useradd -m %s" % user,
                             log_to_file=logfile)

    def _get_checklist(self, cfg):
        """Returns a 4-item (description, user, filename, args) list."""
        l = []
        for checkdata in cfg:
            d = collections.defaultdict(str)
            for k, v in checkdata.items():
                d[k] = v
            l.append((d.get("description", None),
                      d.get("user", None),
                      d.get("test", None),
                      d.get("args", None),
                      d.get("sudo", None)))

        checklist = []
        for check in l:
            description, user, path, args, sudo = check
            if os.path.exists(path):
                if os.path.isdir(path):
                    for f in self._get_files_from_dir(path):
                        checklist.append((description, user, f, args))
                elif os.path.isfile(path):
                    checklist.append(check)
            else:
                api.info(("Could not execute check '%s': no such file or "
                          "directory." % path))

        return checklist

    def _run_checks(self, cfg, logfile):
        """Runs the checks received."""
        failed_checks = []
        for check in self._get_checklist(cfg):
            description, user, f, args, sudo = check
            api.info("Probe '%s'" % description)
            if args:
                if isinstance(args, list):
                    args = ' '.join(args)
            else:
                args = ''
            cmd = "./%s" % " ".join([f, args])
            sudo_user = os.environ.get("SUDO_USER", None)
            _user = None
            if user:
                _user = user
            elif sudo_user:
                _user = sudo_user
            if _user:
                cmd = "su %s -c \"%s\"" % (_user, cmd)

            if not self._is_executable(f):
                api.info("Could not run check '%s': file is not executable"
                         % f)
            else:
                # self._handle_user(_user, logfile)
                sudo_user = sudo or os.environ.get("SUDO_USER", None)
                r = utils.runcmd(cmd,
                                 stderr_to_stdout=True,
                                 log_to_file=logfile,
                                 nosudo=sudo_user)
                if r.failed:
                    failed_checks.append(cmd)
                else:
                    api.info("Command '%s' ran successfully" % cmd)

        return failed_checks

    @qc.qcstep("QC_FUNC_1", "Basic Funcionality Test.")
    def qc_func_1(self, cfg):
        """Basic Funcionality Test."""
        if cfg:
            failed_checks = self._run_checks(cfg, logfile="qc_func_1")
            if failed_checks:
                api.fail("Probes '%s' failed to run." % failed_checks)
            else:
                api.ok("Basic functionality probes ran successfully.")
        else:
            api.na("No definition found for QC_FUNC_1.")

    @qc.qcstep("QC_FUNC_2", "New features/bug fixes testing.")
    def qc_func_2(self, cfg):
        """New features/bug fixes testing."""
        if cfg:
            failed_checks = self._run_checks(cfg, logfile="qc_func_2")
            if failed_checks:
                api.fail("Probes '%s' failed to run." % failed_checks)
            else:
                api.ok("Fix/features probes ran successfully.")
        else:
            api.na("No definition found for QC_FUNC_2.")

    @qc.qcstep_request
    def run(self, steps, *args, **kwargs):
        config.CFG["qc_envvars"] = qc.get_qc_envvars()
        qc_specific_id = utils.to_list(config.CFG["qc_specific_id"])

        if qc_specific_id:
            for id in qc_specific_id:
                try:
                    with open(QC_SPECIFIC_FILE) as f:
                        d = yaml.load(f)
                except IOError:
                    api.info("Could not load QC-specific config file: %s"
                             % QC_SPECIFIC_FILE)
                try:
                    d[id]
                except KeyError:
                    api.info("QC-specific ID '%s' definition not found "
                             "in configuration file '%s'"
                             % (id, QC_SPECIFIC_FILE))

                cfg = collections.defaultdict(dict)
                for k, v in d[id].items():
                    cfg[k] = v

                if steps:
                    for method in steps:
                        method(cfg[method.im_func.func_name])
                else:
                    self.qc_func_1(cfg["qc_func_1"])
                    self.qc_func_2(cfg["qc_func_2"])
        else:
            api.info(("No QC-specific ID provided: no specific QC probes "
                      "will be ran."))

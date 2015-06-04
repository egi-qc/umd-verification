
import collections
import os
import pwd
import yaml

from fabric.api import shell_env

from umd.api import fail
from umd.api import info
from umd.api import ok
from umd.base.utils import QCStep
from umd.config import CFG


QC_SPECIFIC_FILE = "etc/qc_specific.yaml"


class Validate(object):
    def __init__(self):
        self.qc_envvars = None

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

    def _handle_user(self, qc_step, user):
        """Assures that the given user exists (creates it if needed)."""
        try:
            pwd.getpwnam(user)
        except KeyError:
            if user:
                qc_step.runcmd("useradd -m %s" % user)

    def _get_checklist(self, config):
        """Returns a list of 4-item (description, user, filename, args)
           tuples."""
        l = []
        for checkdata in config:
            d = collections.defaultdict(str)
            for k, v in checkdata.items():
                d[k] = v
            l.append((d["description"],
                      d["user"],
                      d["test"],
                      d["args"]))

        checklist = []
        for check in l:
            description, user, path, args = check
            if os.path.isdir(path):
                for f in self._get_files_from_dir(path):
                    checklist.append((description, user, f, args))
            elif os.path.isfile(path):
                checklist.append(check)

        return checklist

    def _run_checks(self, qc_step, config):
        """Runs the checks received."""
        failed_checks = []
        for check in self._get_checklist(config):
            description, user, f, args = check
            info("Probe '%s'" % description)

            cmd = "./%s" % " ".join([f, args])
            if user:
                cmd = ' '.join(["su %s -c" % user, cmd])

            cmd_failed = False
            if not self._is_executable(f):
                info("Could not run check '%s': file is not executable" % f)
                cmd_failed = True
            else:
                self._handle_user(qc_step, user)
                with shell_env(**self.qc_envvars):
                    r = qc_step.runcmd(cmd)
                    cmd_failed = r.failed
                    result = r

            if cmd_failed:
                fail("Command '%s' failed: %s" % (cmd, result))
                failed_checks.append(cmd)
            else:
                ok("Command '%s' ended OK with result: %s"
                   % (cmd, result))
        return failed_checks

    def qc_func_1(self, config):
        """Basic Funcionality Test."""
        qc_step = QCStep("QC_FUNC_1",
                         "Basic Funcionality Test.",
                         os.path.join(CFG["log_path"], "qc_func_1"))

        if config:
            failed_checks = self._run_checks(qc_step, config)
            if failed_checks:
                qc_step.print_result("FAIL",
                                     "Commands failed: %s" % failed_checks,
                                     do_abort=False)
            else:
                qc_step.print_result("OK",
                                     ("Basic functionality probes ran "
                                      "successfully."))
        else:
            qc_step.print_result("OK",
                                 "No definition found for QC_FUNC_1.")

    def qc_func_2(self, config):
        """New features/bug fixes testing."""
        qc_step = QCStep("QC_FUNC_2",
                         "New features/bug fixes testing.",
                         os.path.join(CFG["log_path"], "qc_func_2"))

        if config:
            failed_checks = self._run_checks(qc_step, config)
            if failed_checks:
                qc_step.print_result("FAIL",
                                     "Commands failed: %s" % failed_checks,
                                     do_abort=False)
            else:
                qc_step.print_result("OK",
                                     "Fix/features probes ran successfully.")
        else:
            qc_step.print_result("OK",
                                 "No definition found for QC_FUNC_2.")

    def run(self, qc_specific_id, qc_envvars=None):
        if qc_specific_id:
            try:
                with open(QC_SPECIFIC_FILE) as f:
                    d = yaml.load(f)
            except IOError:
                info("Could not load QC-specific config file: %s"
                     % QC_SPECIFIC_FILE)
            try:
                d[qc_specific_id]
            except KeyError:
                info("QC-specific ID '%s' definition not found "
                     "in configuration file '%s'"
                     % (qc_specific_id, QC_SPECIFIC_FILE))

            config = collections.defaultdict(dict)
            for k, v in d[qc_specific_id].items():
                config[k] = v

            if qc_envvars:
                self.qc_envvars = qc_envvars

            self.qc_func_1(config["qc_func_1"])
            self.qc_func_2(config["qc_func_2"])
        else:
            info(("No QC-specific ID provided: no specific QC probes "
                  "will be ran."))

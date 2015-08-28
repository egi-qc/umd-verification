
import collections
import os
import pwd

from fabric import api as fabric_api
import yaml

from umd import api
from umd.base import utils as butils
from umd import config


# FIXME Move to defaults.yaml
QC_SPECIFIC_FILE = "etc/qc_specific.yaml"


class Validate(object):
    def __init__(self):
        self.qc_envvars = butils.get_qc_envvars()

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

    def _get_checklist(self, cfg):
        """Returns a 4-item (description, user, filename, args) list."""
        l = []
        for checkdata in cfg:
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

    def _run_checks(self, qc_step, cfg):
        """Runs the checks received."""
        failed_checks = []
        for check in self._get_checklist(cfg):
            description, user, f, args = check
            api.info("Probe '%s'" % description)

            cmd = "./%s" % " ".join([f, args])
            if user:
                cmd = "su %s -c \"%s\"" % (user, cmd)

            if not self._is_executable(f):
                api.info("Could not run check '%s': file is not executable"
                         % f)
            else:
                self._handle_user(qc_step, user)
                with fabric_api.shell_env(**self.qc_envvars):
                    r = qc_step.runcmd(cmd,
                                       fail_check=False,
                                       stderr_to_stdout=True)
                    if r.failed:
                        failed_checks.append(cmd)
                    else:
                        api.info("Command '%s' ran successfully" % cmd)

        return failed_checks

    def qc_func_1(self, cfg):
        """Basic Funcionality Test."""
        qc_step = butils.QCStep("QC_FUNC_1",
                                "Basic Funcionality Test.",
                                "qc_func_1")

        if cfg:
            failed_checks = self._run_checks(qc_step, cfg)
            if failed_checks:
                qc_step.print_result("FAIL",
                                     "Probes '%s' failed to run."
                                     % failed_checks)
            else:
                qc_step.print_result("OK",
                                     ("Basic functionality probes ran "
                                      "successfully."))
        else:
            qc_step.print_result("NA",
                                 "No definition found for QC_FUNC_1.")

    def qc_func_2(self, cfg):
        """New features/bug fixes testing."""
        qc_step = butils.QCStep("QC_FUNC_2",
                                "New features/bug fixes testing.",
                                "qc_func_2")

        if cfg:
            failed_checks = self._run_checks(qc_step, cfg)
            if failed_checks:
                qc_step.print_result("FAIL",
                                     "Probes '%s' failed to run."
                                     % failed_checks)
            else:
                qc_step.print_result("OK",
                                     "Fix/features probes ran successfully.")
        else:
            qc_step.print_result("NA",
                                 "No definition found for QC_FUNC_2.")

    @butils.qcstep_request
    def run(self, steps, *args, **kwargs):
        qc_specific_id = config.CFG["qc_specific_id"]
        if qc_specific_id:
            try:
                with open(QC_SPECIFIC_FILE) as f:
                    d = yaml.load(f)
            except IOError:
                api.info("Could not load QC-specific config file: %s"
                         % QC_SPECIFIC_FILE)
            try:
                d[qc_specific_id]
            except KeyError:
                api.info("QC-specific ID '%s' definition not found "
                         "in configuration file '%s'"
                         % (qc_specific_id, QC_SPECIFIC_FILE))

            cfg = collections.defaultdict(dict)
            for k, v in d[qc_specific_id].items():
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

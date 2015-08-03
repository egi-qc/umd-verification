import os.path

from umd.base.security import utils as sec_utils
from umd.base.utils import QCStep
from umd.base.utils import qcstep_request
from umd.config import CFG


class Security(object):
    def __init__(self):
        self.cfgtool = CFG["cfgtool"]
        self.need_cert = CFG["need_cert"]
        self.ca = CFG["ca"]
        self.exceptions = CFG["exceptions"] # known_worldwritable_filelist:
                                            # list with the known world
                                            # writable files.

    def qc_sec_2(self):
        """SHA-2 Certificates Support."""
        qc_step = QCStep("QC_SEC_2",
                         "SHA-2 Certificates Support",
                         os.path.join(CFG["log_path"], "qc_sec_2"))

        if self.need_cert:
            self.ca.issue_cert(hash="2048",
                               key_prv="/etc/grid-security/hostkey.pem",
                               key_pub="/etc/grid-security/hostcert.pem")

            r = self.cfgtool.run()
            if r and r.failed:
                qc_step.print_result("FAIL",
                                     "YAIM configuration failed with SHA-2 "
                                     "certs.",
                                     do_abort=True)
            else:
                qc_step.print_result("OK",
                                     "Product services can manage SHA-2 "
                                     "certs.")
        else:
            qc_step.print_result("NA", "Product does not need certificates.")

    def qc_sec_5(self):
        """World Writable Files check."""
        qc_step = QCStep("QC_SEC_5",
                         "World Writable Files",
                         os.path.join(CFG["log_path"], "qc_sec_5"))

        r = qc_step.runcmd(("find / -not \\( -path \"/proc\" -prune \\) "
                            "-type f -perm -002 -exec ls -l {} \;"),
                           fail_check=False)
        if r:
            ww_filelist = sec_utils.get_filelist_from_find(r)
            try:
                known_ww_filelist = self.exceptions[
                        "known_worldwritable_filelist"]
            except KeyError:
                known_ww_filelist = []
            if set(ww_filelist).difference(set(known_ww_filelist)):
                qc_step.print_result("FAIL",
                                     "Found %s world-writable file/s."
                                     % len(ww_filelist),
                                     do_abort=True)
            else:
                qc_step.print_result("WARNING",
                                     ("Found world-writable file/s "
                                      "required for operation."))
        else:
            qc_step.print_result("OK",
                                 "Found no world-writable file.")

        # if self.pkgtool.os == "sl5":
        #     pkg_wwf_files = local(("rpm -qalv | egrep '^[-d]([-r][-w][-xs])"
        #                            "{2}[-r]w'"))
        #     if pkg_wwf_files:
        #         print(yellow("Detected package world-writable files:\n%s"
        #                      % pkg_wwf_files))

    @qcstep_request
    def run(self, steps, *args, **kwargs):
        if steps:
            for method in steps:
                method()
        else:
            self.qc_sec_2()
            self.qc_sec_5()

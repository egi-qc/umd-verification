from umd import api
from umd.base.security import utils as sec_utils
from umd.common import qc
from umd import config
from umd import utils


class Security(object):
    def __init__(self):
        self.cfgtool = config.CFG["cfgtool"]
        self.need_cert = config.CFG["need_cert"]
        self.ca = config.CFG["ca"]
        # exceptions
        #   'known_worldwritable_filelist': already-known world writable files
        self.exceptions = config.CFG["exceptions"]

    @qc.qcstep("QC_SEC_2", "SHA-2 Certificates Support")
    def qc_sec_2(self):
        """SHA-2 Certificates Support."""
        if self.need_cert:
            if not self.cfgtool:
                api.warn(("SHA-2 management not tested: configuration tool "
                          "not defined."))
            else:
                if not self.cfgtool.has_run:
                    r = self.cfgtool.run()
                    if r.failed:
                        api.fail("Configuration failed with SHA-2 certs",
                                 stop_on_error=True)
                    else:
                        api.ok("Product services can manage SHA-2 certs.")
        else:
            api.na("Product does not need certificates.")

    @qc.qcstep("QC_SEC_5", "World Writable Files")
    def qc_sec_5(self):
        """World Writable Files check."""
        _logfile = "qc_sec_5"

        r = utils.runcmd(("find / -not \\( -path \"/proc\" -prune \\) "
                          "-not \\( -path \"/sys\" -prune \\) "
                          "-type f -perm -002 -exec ls -l {} \;"),
                         log_to_file=_logfile)
        if r:
            ww_filelist = sec_utils.get_filelist_from_find(r)
            try:
                known_ww_filelist = self.exceptions[
                    "known_worldwritable_filelist"]
            except KeyError:
                known_ww_filelist = []
            if set(ww_filelist).difference(set(known_ww_filelist)):
                api.fail("Found %s world-writable file/s." % len(ww_filelist),
                         logfile=r.logfile)
            else:
                api.warn("Found world-writable file/s required for operation.",
                         logfile=r.logfile)
        else:
            api.ok("Found no world-writable file.")

        # if self.pkgtool.os == "sl5":
        #     pkg_wwf_files = local(("rpm -qalv | egrep '^[-d]([-r][-w][-xs])"
        #                            "{2}[-r]w'"))
        #     if pkg_wwf_files:
        #         print(yellow("Detected package world-writable files:\n%s"
        #                      % pkg_wwf_files))

    @qc.qcstep_request
    def run(self, steps, *args, **kwargs):
        if steps:
            for method in steps:
                method()
        else:
            self.qc_sec_2()
            self.qc_sec_5()

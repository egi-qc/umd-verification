import ldap

import time

from umd import api
from umd.base.infomodel import utils as info_utils
from umd.base import utils as butils
from umd import config
from umd import exception
from umd import system
from umd import utils


def bdii_support(f):
    def _support(self, *args, **kwargs):
        if self.has_infomodel:
            if self.cfgtool:
                if not self.cfgtool.has_run:
                    r = self.cfgtool.run()
                    if r.failed:
                        api.fail("Fail while running configuration tool",
                                 stop_on_error=True)
            return f(self, *args, **kwargs)

        api.na("Product does not publish information through BDII.")
    return _support


class InfoModel(object):
    def __init__(self):
        self.cfgtool = config.CFG["cfgtool"]
        self.has_infomodel = config.CFG["has_infomodel"]
        self.attempt_no = 5
        self.attempt_sleep = 60

        # NOTE(orviz): within a QCStep?
        utils.install("glue-validator")
        if system.distro_version == "redhat5":
            utils.install("openldap-clients")

    def _set_breathe_time(self):
        # FIXME(orviz) This should be handled by the Puppet module
        breathe_time = 30
        utils.runcmd(("sed -i 's/^BDII_BREATHE_TIME.*/BDII_BREATHE_TIME=%s/g' "
                      "/etc/bdii/bdii.conf" % breathe_time))
        utils.runcmd("/etc/init.d/bdii restart")

    def _run_validator(self, glue_version, logfile):
        port = config.CFG.get("info_port", "2170")
        if glue_version == "glue1":
            cmd = ("glue-validator -H localhost -p %s -b "
                   "mds-vo-name=resource,o=grid -g glue1 -s "
                   "general -v 3" % port)
            version = "1.3"
        elif glue_version == "glue2":
            cmd = ("glue-validator -H localhost -p %s -b "
                   "GLUE2GroupID=resource,o=glue -g glue2 -s general -v 3"
                   % port)
            version = "2.0"

        self._set_breathe_time()

        slapd_working = False
        for attempt in xrange(self.attempt_no):
            r = utils.runcmd(cmd, log_to_file=logfile)
            if not r.failed:
                slapd_working = True
                break
            else:
                time.sleep(self.attempt_sleep)
        if not slapd_working:
            api.fail("Could not connect to LDAP service.", stop_on_error=True)

        summary = info_utils.get_gluevalidator_summary(r)
        if summary:
            if summary["errors"] != '0':
                api.fail(("Found %s errors while validating GlueSchema "
                          "v%s support" % (summary["errors"], version)),
                         logfile=r.logfile)
            elif summary["warnings"] != '0':
                api.warn(("Found %s warnings while validating GlueSchema "
                          "v%s support" % (summary["warnings"], version)))
            else:
                api.ok(("Found no errors or warnings while validating "
                        "GlueSchema v%s support" % version))
        else:
            raise exception.InfoModelException(("Cannot parse "
                                                "glue-validator output: %s"
                                                % r))

    def _run_version_check(self, logfile):
        port = config.CFG.get("info_port", "2170")
        conn = ldap.initialize("ldap://localhost:%s" % port)
        try:
            ldap_result = conn.search_s(
                "GLUE2GroupID=resource,o=glue",
                ldap.SCOPE_SUBTREE,
                "objectclass=GLUE2Endpoint",
                attrlist=[
                    "GLUE2EndpointImplementationVersion",
                    "GLUE2EntityOtherInfo"])

            utils.to_file(info_utils.ldifize(ldap_result), logfile)

            version_list = []
            for dn, attrs in ldap_result:
                try:
                    version_list = attrs["GLUE2EndpointImplementationVersion"]
                except KeyError:
                    return False, ("No implementation version found for DN: "
                                   "%s" % dn)
                try:
                    d = dict([attr.split('=', 1)
                              for attr in attrs["GLUE2EntityOtherInfo"]])
                    version_list.append(d["MiddlewareVersion"])
                except KeyError:
                    return False, "No middleware version found for DN: %s" % dn

                for version in version_list:
                    if not info_utils.validate_version(version):
                        return False, "Found a non-valid version: %s" % version
            return True, "Middleware versions found: %s" % version_list
        finally:
            conn.unbind_s()

    @butils.qcstep("QC_INFO_1", "GlueSchema 1.3 Support")
    @bdii_support
    def qc_info_1(self):
        """GlueSchema 1.3 Support."""
        self._run_validator("glue1", logfile="qc_info_1")

    @butils.qcstep("QC_INFO_2", "GlueSchema 2.0 Support")
    @bdii_support
    def qc_info_2(self):
        """GlueSchema 2.0 Support."""
        self._run_validator("glue2", logfile="qc_info_2")

    @butils.qcstep("QC_INFO_3", "Middleware Version Information")
    @bdii_support
    def qc_info_3(self):
        """Middleware Version Information."""
        r, msg = self._run_version_check(logfile="qc_info_3")
        if r:
            api.ok(msg)
        else:
            api.warn(msg)

    @butils.qcstep_request
    def run(self, steps, *args, **kwargs):
        if steps:
            for method in steps:
                method()
        else:
            self.qc_info_1()
            self.qc_info_2()
            self.qc_info_3()

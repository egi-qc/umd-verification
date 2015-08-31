import ldap

from umd.base.infomodel import utils as info_utils
from umd.base import utils as butils
from umd import config
from umd import exception
from umd import system
from umd import utils


def bdii_support(f):
    def _support(self, *args, **kwargs):
        if f.func_name == "qc_info_1":
            qc_step = butils.QCStep("QC_INFO_1",
                                    "GlueSchema 1.3 Support",
                                    "qc_info_1")
        elif f.func_name == "qc_info_2":
            qc_step = butils.QCStep("QC_INFO_2",
                                    "GlueSchema 2.0 Support",
                                    "qc_info_2")
        elif f.func_name == "qc_info_3":
            qc_step = butils.QCStep("QC_INFO_3",
                                    "Middleware Version Information",
                                    "qc_info_3")

        if self.has_infomodel:
            if self.cfgtool:
                if not self.cfgtool.has_run:
                    self.cfgtool.run(qc_step)
            return f(self, qc_step, *args, **kwargs)

        qc_step.print_result("NA", ("Product does not publish information "
                                    "through BDII."))
    return _support


class InfoModel(object):
    def __init__(self):
        self.cfgtool = config.CFG["cfgtool"]
        self.has_infomodel = config.CFG["has_infomodel"]

        # NOTE(orviz): within a QCStep?
        utils.install("glue-validator")
        if system.distro_version == "redhat5":
            utils.install("openldap-clients")

    def _run_validator(self, qc_step, glue_version):
        # if self.has_infomodel:
            if glue_version == "glue1":
                cmd = ("glue-validator -H localhost -p 2170 -b o=grid "
                       "-g glue1 -s general -v 3")
                version = "1.3"
            elif glue_version == "glue2":
                cmd = ("glue-validator -H localhost -p 2170 -b o=glue "
                       "-g glue2 -s general -v 3")
                version = "2.0"

            r = qc_step.runcmd(cmd, fail_check=False)
            summary = info_utils.get_gluevalidator_summary(r)
            if summary:
                if summary["errors"] != '0':
                    qc_step.print_result("FAIL",
                                         ("Found %s errors while validating "
                                          "GlueSchema v%s support"
                                          % (summary["errors"]), version),
                                         do_abort=True)
                elif summary["warnings"] != '0':
                    qc_step.print_result("WARNING",
                                         ("Found %s warnings while validating "
                                          "GlueSchema v%s support"
                                          % (summary["warnings"], version)))
                else:
                    qc_step.print_result("OK",
                                         ("Found no errors or warnings while "
                                          "validating GlueSchema v%s support"
                                          % version))
            else:
                raise exception.InfoModelException(("Cannot parse "
                                                    "glue-validator output: %s"
                                                    % r))
        # else:
        #     qc_step.print_result("NA", ("Product does not publish "
        #                                 "information through BDII."))

    def _run_version_check(self, qc_step):
        conn = ldap.initialize("ldap://localhost:2170")
        try:
            ldap_result = conn.search_s(
                "GLUE2GroupID=resource,o=glue",
                ldap.SCOPE_SUBTREE,
                "objectclass=GLUE2Endpoint",
                attrlist=[
                    "GLUE2EndpointImplementationVersion",
                    "GLUE2EntityOtherInfo"])

            utils.to_file(info_utils.ldifize(ldap_result), qc_step.logfile)

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
            return True
        finally:
            conn.unbind_s()

    @bdii_support
    def qc_info_1(self, qc_step):
        """GlueSchema 1.3 Support."""
        self._run_validator(qc_step, "glue1")

    @bdii_support
    def qc_info_2(self, qc_step):
        """GlueSchema 2.0 Support."""
        self._run_validator(qc_step, "glue2")

    @bdii_support
    def qc_info_3(self, qc_step):
        """Middleware Version Information."""
        r, msg = self._run_version_check(qc_step)
        if r:
            qc_step.print_result("OK", msg)
        else:
            qc_step.print_result("WARNING", msg)

    @butils.qcstep_request
    def run(self, steps, *args, **kwargs):
        if steps:
            for method in steps:
                method()
        else:
            self.qc_info_1()
            self.qc_info_2()
            self.qc_info_3()

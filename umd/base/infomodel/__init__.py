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

import ldap

import time

from umd import api
from umd.base.infomodel import utils as info_utils
from umd.common import qc
from umd import config
# from umd import exception
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

    def _set_breathe_time(self):
        # FIXME(orviz) This should be handled by the Puppet module
        breathe_time = 30
        utils.runcmd(("sed -i 's/^BDII_BREATHE_TIME.*/BDII_BREATHE_TIME=%s/g' "
                      "/etc/bdii/bdii.conf" % breathe_time))
        utils.runcmd("/etc/init.d/bdii restart")

    def _run_validator(self, glue_version, logfile):
        # NOTE(orviz): within a QCStep?
        utils.install("glue-validator")
        if system.distro_version == "redhat5":
            utils.install("openldap-clients")

        port = config.CFG.get("info_port", "2170")
        if glue_version == "glue1":
            #cmd = ("glue-validator -h localhost -p %s -b "
            #       "mds-vo-name=resource,o=grid -t glue1" % port)
            cmd = ("glue-validator -H localhost -p %s -b "
                   "o=glue -g glue1 -s general" % port)
            version = "1.3"
        elif glue_version == "glue2":
            #cmd = ("glue-validator -h localhost -p %s -b "
            #       "GLUE2GroupID=resource,o=glue -t glue2" % port)
            cmd = ("glue-validator -H localhost -p %s -b "
                   "o=glue -g glue2 -s general" % port)
            version = "2.0"

        time.sleep(self.attempt_sleep)

        breathe_time_set = False
        slapd_working = False
        summary = None
        for attempt in xrange(self.attempt_no):
            r = utils.runcmd(cmd, log_to_file=logfile)
            if not r.failed:
                summary = {}
                if r:
                    summary = info_utils.get_gluevalidator_summary(r)
                slapd_working = True
                break
            else:
                if not breathe_time_set:
                    self._set_breathe_time()
                    breathe_time_set = True
                time.sleep(self.attempt_sleep)
        if not slapd_working:
            api.fail("Could not connect to LDAP service.", stop_on_error=True)

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
        # else:
        #     raise exception.InfoModelException(("Cannot parse "
        #                                         "glue-validator output: %s"
        #                                         % r))

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

    @qc.qcstep("QC_INFO_1", "GlueSchema 1.3 Support")
    @bdii_support
    def qc_info_1(self):
        """GlueSchema 1.3 Support."""
        self._run_validator("glue1", logfile="qc_info_1")

    @qc.qcstep("QC_INFO_2", "GlueSchema 2.0 Support")
    @bdii_support
    def qc_info_2(self):
        """GlueSchema 2.0 Support."""
        self._run_validator("glue2", logfile="qc_info_2")

    @qc.qcstep("QC_INFO_3", "Middleware Version Information")
    @bdii_support
    def qc_info_3(self):
        """Middleware Version Information."""
        r, msg = self._run_version_check(logfile="qc_info_3")
        if r:
            api.ok(msg)
        else:
            api.warn(msg)

    @qc.qcstep_request
    def run(self, steps, *args, **kwargs):
        if steps:
            for method in steps:
                method()
        else:
            self.qc_info_1()
            self.qc_info_2()
            self.qc_info_3()

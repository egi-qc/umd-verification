import json
import os.path
import requests

from umd.base.utils import QCStep
from umd.base.utils import qcstep_request
from umd.config import CFG


class Operations(object):
    def qc_mon_1(self):
        """Service Probes."""
        qc_step = QCStep("QC_MON_1",
                         "Service Probes",
                         os.path.join(CFG["log_path"], "qc_mon_1"))

        if CFG["qc_mon_capable"]:
            headers = {"content-type": "application/json"}
            url = "http://%s/siteurls" % CFG["umdnsu_url"]
            data = {"name": CFG["name"].upper()}

            try:
                resp = requests.post(url, data=json.dumps(data), headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    if data["enabled"]:
                        # FIXME Need to provide the Nagios URL where the host will
                        # be monitored
                        qc_step.print_result("OK",
                                             "LDAP URL added:'%s %s'"
                                              % (data["prefix"], data["url"]))
                    else:
                        qc_step.print_result("WARN",
                                             "Could not add LDAP URL: %s"
                                             % resp.text)
                else:
                    qc_step.print_result("FAIL",
                                         ("Response error received from server (%s): "
                                          "'%s'") % (resp.status_code, resp.text))
            except requests.exceptions.ConnectionError:
                qc_step.print_result("FAIL",
                                     "Could not connect to Nagios at '%s'" % url)
        else:
            qc_step.print_result("NA", "Product cannot be tested by Nagios.")


    @qcstep_request
    def run(self, steps, *args, **kwargs):
        if steps:
            for method in steps:
                method()
        else:
            self.qc_mon_1()

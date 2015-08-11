import grp
import pwd

from umd import api
from umd import base
from umd import utils


class GLExecWNDeploy(base.Deploy):
    def post_install(self):
        s_groups = [t[0] for t in grp.getgrall()]
        s_users = [t[0] for t in pwd.getpwall()]

        api.info("Configuration actions.")

        if "iberops" not in s_groups:
            utils.runcmd("groupadd -g 23200 iberops")
        for i in xrange(5):
            user = "iberops00%s" % i
            if user not in s_users:
                utils.runcmd("useradd -m -u 2320%s -g 23200 %s" % (i, user))
        api.info("Group 'iberops' and user accounts created.")

        if "iberopses" not in s_groups:
            utils.runcmd("groupadd -g 23210 iberopses")
        for i in xrange(5):
            user = "iberopses00%s" % i
            if user not in s_users:
                utils.runcmd("useradd -m -u 2321%s -g 23210 %s" % (i, user))
        api.info("Group 'iberopses' and user accounts created.")

        utils.runcmd("cp /etc/glexec.conf /etc/glexec.conf.0")
        api.info("Backup /etc/glexec.conf file.")
        utils.runcmd(("sed -i 's/.*user_white_list.*/user_white_list = umd/g' "
                      "/etc/glexec.conf"))
        api.info("User 'umd' white-listed in /etc/glexec.conf")

        utils.runcmd(("cp /etc/lcmaps/lcmaps-glexec.db "
                      "/etc/lcmaps/lcmaps-glexec.db.0"))
        api.info("Backup /etc/lcmaps/lcmaps-glexec.db file.")
        lcmaps_db = """
# where to look for modules
path = /usr/lib64/lcmaps

# module definitions
verify_proxy = "lcmaps_verify_proxy.mod"
               " -certdir /etc/grid-security/certificates/"
               " --allow-limited-proxy"

pepc = "lcmaps_c_pep.mod"
       "--pep-daemon-endpoint-url https://amargus02.ifca.es:8154/authz"
       " -resourceid http://authz-interop.org/xacml/resource/resource-type/wn"
       " -actionid http://glite.org/xacml/action/execute"
       " -capath /etc/grid-security/certificates/"
       " -pep-certificate-mode implicit"
       " --use-pilot-proxy-as-cafile" # Add this on RHEL 6 based systems

glexec_get_account:
verify_proxy -> pepc
        """
        with open("/etc/lcmaps/lcmaps-glexec.db", 'w') as f:
            f.write(lcmaps_db)
        api.info("GLExec lcmaps configured.")

    def pre_validate(self):
        api.info("PRE-validate actions.")
        utils.install(["myproxy", "voms-clients", "ca-policy-egi-core"])


glexec_wn = GLExecWNDeploy(
    name="glexec-wn",
    doc="GLExec WN deployment.",
    metapkg=["glexec-wn"],
    qc_specific_id="glexec-wn"
)

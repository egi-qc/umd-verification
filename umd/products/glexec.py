from umd.api import info
from umd.base import Deploy
from umd.utils import install
from umd.utils import runcmd


class GlexecDeploy(Deploy):
    def _config(self):
        info("Configuration actions.")

        runcmd("groupadd -g 23200 iberops")
        for i in xrange(5):
            runcmd("useradd -m -u 2320%s -g 23200 iberops00%s" % (i, i))
        info("Group 'iberops' and user accounts created.")

        runcmd("groupadd -g 23210 iberopses")
        for i in xrange(5):
            runcmd("useradd -m -u 2321%s -g 23210 iberopses00%s" % (i, i))
        info("Group 'iberopses' and user accounts created.")

        runcmd("cp /etc/glexec.conf /etc/glexec.conf.0")
        info("Backup /etc/glexec.conf file.")
        runcmd(("sed -i 's/.*user_white_list.*/user_white_list = umd/g'"
                "/etc/glexec.conf"))
        info("User 'umd' white-listed in /etc/glexec.conf")

        runcmd(("cp /etc/lcmaps/lcmaps-glexec.db "
                "/etc/lcmaps/lcmaps-glexec.db.0"))
        info("Backup /etc/lcmaps/lcmaps-glexec.db file.")
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
        info("GLExec lcmaps configured.")

    def pre_validate(self):
        info("PRE-validate actions.")
        install(["myproxy", "voms-clients", "ca-policy-egi-core"])


glexec = GlexecDeploy(
    name="glexec",
    doc="GLEXEC deployment.",
    metapkg=["glexec",
             "lcmaps-plugins-c-pep",
             "lcmaps-plugins-c-pep-debuginfo",
             "mkgltempdir",
             "lcmaps-plugins-verify-proxy"],
    need_cert=False,
    qc_specific_id="glexec"
)

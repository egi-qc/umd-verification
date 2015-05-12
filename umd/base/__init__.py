from fabric.tasks import Task

from umd.base.configure import YaimConfig
from umd.base.infomodel import InfoModel
from umd.base.install import Install
from umd.base.install import utils as inst_utils
from umd.base.security import Security
from umd.base import utils
from umd.base.validate import Validate
from umd.config import CFG
from umd import exception


class Deploy(Task):
    """Base class for UMD deployments."""
    def __init__(self,
                 name,
                 doc=None,
                 metapkg=[],
                 need_cert=False,
                 nodetype=[],
                 siteinfo=[],
                 qc_specific_id=None,
                 exceptions={}):
        """Arguments:
                name: Fabric command name.
                doc: docstring that will appear when typing `fab -l`.
                metapkg: list of UMD metapackages to install.
                need_cert: whether installation type requires a signed cert.
                nodetype: list of YAIM nodetypes to be configured.
                siteinfo: list of site-info files to be used.
                qc_specific_id: ID that match the list of QC-specific checks
                    to be executed. The check definition must be included in
                    etc/qc_specific.yaml
                exceptions: documented exceptions for a given UMD product.
        """
        self.name = name
        if doc:
            self.__doc__ = doc
        self.metapkg = metapkg
        self.need_cert = need_cert
        self.nodetype = nodetype
        self.siteinfo = siteinfo
        self.qc_specific_id = qc_specific_id
        self.exceptions = exceptions
        self.pkgtool = None
        self.cfgtool = None
        self.ca = None

    def pre_install(self):
        pass

    def post_install(self):
        pass

    def pre_config(self):
        pass

    def post_config(self):
        pass

    def pre_validate(self):
        pass

    def post_validate(self):
        pass

    def _install(self, *args, **kwargs):
        Install(self.pkgtool,
                self.metapkg).run(*args, **kwargs)

    def _security(self, *args, **kwargs):
        Security(self.pkgtool,
                 self.cfgtool,
                 self.need_cert,
                 self.ca,
                 self.exceptions).run(*args, **kwargs)

    def _infomodel(self, *args, **kwargs):
        InfoModel(self.pkgtool,
                  self.cfgtool).run(*args, **kwargs)

    def _validate(self, *args, **kwargs):
        Validate().run(self.qc_specific_id, *args, **kwargs)

    def _get_qc_envvars(self, d):
        return dict([(k.split("qcenv_")[1], v)
                     for k, v in d.items() if k.startswith("qcenv")])

    def run(self,
            installation_type,
            **kwargs):
        """Takes over base deployment.

        Arguments:
            installation_type
                Type of installation: 'install' (from scratch) or 'update'.

        Keyword arguments (optional, takes default from etc/defaults.yaml):
            repository_url
                Repository path with the verification content.
            epel_release
                Package URL with the EPEL release.
            umd_release
                Package URL with the UMD release.
            igtf_repo
                Repository for the IGTF release.
            yaim_path
                Path pointing to YAIM configuration files.
            log_path
                Path to store logs produced during the execution.
            qcenv_*
                Pass environment variables needed by the QC specific checks.
        """
        # Update configuration
        CFG.update(kwargs)

        # Packaging tool
        self.pkgtool = inst_utils.PkgTool()

        # Configuration tool
        if self.nodetype and self.siteinfo:
            self.cfgtool = YaimConfig(self.nodetype,
                                      self.siteinfo,
                                      CFG["yaim_path"],
                                      pre_config=self.pre_config,
                                      post_config=self.post_config)
        else:
            raise exception.ConfigException("Configuration not implemented.")

        # Certification Authority
        if self.need_cert:
            self.pkgtool.install(
                pkgs=["ca-policy-egi-core"],
                repofile=CFG["igtf_repo"])
            self.ca = utils.OwnCA(
                domain_comp_country="es",
                domain_comp="UMDverification",
                common_name="UMDVerificationOwnCA")
            self.ca.create(trusted_ca_dir="/etc/grid-security/certificates")

        # QC_INST, QC_UPGRADE
        self.pre_install()
        self._install(installation_type,
                      CFG["epel_release"],
                      CFG["umd_release"],
                      repository_url=CFG["repository_url"])
        self.post_install()

        # QC_SEC
        self._security()

        # QC_INFO
        self._infomodel()

        # QC_FUNC
        qc_envvars = self._get_qc_envvars(kwargs)
        self.pre_validate()
        self._validate(qc_envvars)
        self.post_validate()

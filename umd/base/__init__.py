from fabric import tasks

from umd import api
from umd.base.infomodel import InfoModel
from umd.base.operations import Operations
from umd.base.security import Security
from umd.base.validate import Validate
from umd.common import pki
from umd import config
from umd import utils


class Deploy(tasks.Task):
    """Base class for UMD deployments."""
    def __init__(self,
                 name,
                 doc=None,
                 need_cert=False,
                 has_infomodel=False,
                 cfgtool=None,
                 qc_mon_capable=False,
                 qc_specific_id=[],
                 qc_step=[],
                 exceptions={},
                 dryrun=False,
                 info_port="2170"):
        """Arguments:

                name: Fabric command name.
                doc: docstring that will appear when typing `fab -l`.
                need_cert: whether installation type requires a signed cert.
                has_infomodel: whether the product publishes information
                               about itself.
                cfgtool: configuration tool object.
                qc_specific_id: ID that match the list of QC-specific checks
                    to be executed. The check definition must be included in
                    etc/qc_specific.yaml
                exceptions: documented exceptions for a given UMD product.
                dry_run: list commands, not run them
                info_port: port where information model is published.
        """
        self.name = name
        if doc:
            self.__doc__ = doc
        self.need_cert = need_cert
        self.has_infomodel = has_infomodel
        self.qc_specific_id = qc_specific_id
        self.exceptions = exceptions
        self.cfgtool = cfgtool
        self.qc_mon_capable = qc_mon_capable
        self.qc_envvars = {}
        self.qc_step = qc_step
        self.dryrun = dryrun
        self.info_port = info_port

    def pre_config(self):
        pass

    def post_config(self):
        pass

    def pre_validate(self):
        pass

    def post_validate(self):
        pass

    def _config(self, **kwargs):
        if config.CFG["cfgtool"]:
            if not self.cfgtool.has_run:
                api.info("Running configuration")
                self.cfgtool.run()

    def _security(self, **kwargs):
        Security().run(**kwargs)

    def _infomodel(self, **kwargs):
        InfoModel().run(**kwargs)

    def _operations(self, **kwargs):
        Operations().run(**kwargs)

    def _validate(self, **kwargs):
        self.pre_validate()
        Validate().run(**kwargs)
        self.post_validate()

    def run(self, **kwargs):
        """Takes over base deployment.

        :repository_url: Repository path with the verification content. Could
            pass multiple values by prefixing with 'repository_url'.
        :repository_file: URL pointing to a repository file. Could
            pass multiple values by prefixing with 'repository_file'.
        :umd_release: Package URL with the UMD release.
        :igtf_repo: Repository for the IGTF release.
        :yaim_path: Path pointing to YAIM configuration files.
        :log_path: Path to store logs produced during the execution.
        :qcenv_*: Pass environment variables needed by the QC specific checks.
        :qc_step: Run a given set of Quality Criteria steps. Works exactly as
            'repository_url' i.e. to pass more than one QC step to run, prefix
            it as 'qc_step'.
        :hostcert: Public key server certificate.
        :hostkey: Private key server certificate.
        :package: Custom individual package/s to install.
        :func_id: Functional test/s to be performed ('id' from
            etc/qc_specific.yaml)
        :enable_testing_repo: Enable the UMD or CMD testing repository.
        """
        # Get configuration parameters
        config.CFG.set_defaults()
        config.CFG.update(utils.get_class_attrs(self))
        config.CFG.update(kwargs)

        # Validate configuration
        config.CFG.validate()

        # Show configuration summary
        utils.show_exec_banner_ascii()

        # Workspace
        utils.create_workspace()

        # Configuration tool
        if config.CFG["cfgtool"]:
            config.CFG["cfgtool"].pre_config = self.pre_config
            config.CFG["cfgtool"].post_config = self.post_config

        # Create private & public key
        if self.need_cert:
            pki.certify()

        # Run deployment
        self._config()

        if config.CFG["qc_step"]:
            for step in config.CFG["qc_step"]:
                k, v = (step.rsplit('_', 1)[0], step)
                try:
                    step_mappings = {
                        "QC_SEC": self._security,
                        "QC_INFO": self._infomodel,
                        "QC_FUNC": self._validate}
                except KeyError:
                    api.fail("%s step not found in the Quality Criteria" % k,
                             stop_on_error=True)

                step_mappings[k](**{"qc_step": v})
        else:
            # QC_SEC
            self._security()

            # QC_INFO
            self._infomodel()

            # QC_MON
            self._operations()

            # QC_FUNC
            self._validate()

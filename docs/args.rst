
.. _argument-passing-label:
Argument passing
================


Runtime args
------------

Runtime arguments are given through `fab` argument list. Currently supported
runtime arguments are:


:installation_type: Type of installation.

                - Additional info: available options:

                    :install: from scratch installation, launches
                        `QC_DIST_1 <http://egi-qc.github.io/#INSTALLATION>`_.
                    :update: update from last production version, launches
                        `QC_UPGRADE_1 <http://egi-qc.github.io/#INSTALLATION>`_.

:repository_url: Repository path with the verification content.

                - Additional info: multiple values are allowed by prefixing
                  with `repository_url`.

:umd_release: Package URL with the UMD release.
                - Default value: *required*.

:epel_release: Package URL with the EPEL release (RPM file).

                - Additional info: only available for RedHat-based
                  distributions.

:igtf_repo: Repository for the IGTF release.

                - Default value: *required*.

:yaim_path: Path pointing to YAIM configuration files.

                - Default value: ``etc/yaim/``.

:log_path: Path to store logs produced during the execution.

                - Default value: ``/var/tmp/umd-verification``.

:qcenv_*: Pass environment variables needed by the QC specific checks.

                - Additional info: environment variable name to be exported
                  is the name given after the underscore '_' symbol. The
                  variable's value is the `fab` argument's value. E.g.:
                  - ``qcenv_FOO=bar`` will set ``FOO=bar``.

:qc_step: Run a given set of Quality Criteria steps.

                - Additional info: multiple values are allowed by prefixing
                  with `qc_step`.

:umdnsu_url: URL (hostname:port) to interface with `umdnsu` service running
             in the SAM-Nagios instance.


Static args
-----------

An additional way to provide the runtime arguments seen above is through the
configuration file `etc/defaults.yaml`.

This file *must* exist since it is here where the *required* arguments are set.
This is why it lives within the application codebase.

The format is YAML so the naming of the runtime arguments seen above differ a
little. Currently supported runtime arguments (and their YAML formatted
equivalent) are:

:base\:log_path: ``log_path`` argument.
:epel_release\:<distro_version (e.g. redhat5)>: ``epel_release`` argument.
:umd_release\:<distro_version (e.g. redhat5)>: ``umd_release`` argument.
:igtf_repo\:<distname (e.g. redhat)>: ``igtf_repo``.
:yaim\:path: ``yaim_path``.
:nagios\:umdnsu_url: ``umdnsu_url``.


Instantiation args
------------------

These arguments are used when defining a new deployment (``umd.base.Deploy``
instance) in the product's directory `umd/products`. Currently supported
instantiation arguments are:


:name: UMD product (aka Fabric command name).

       - Type: ``str``.
       - Default value: empty string.

:doc: Docstring that will appear when typing `fab -l`.

       - Type: ``str``.
       - Default value: empty string.

:metapkg: UMD metapackages to install.

       - Type: ``list``.
       - Default value: empty list.

:need_cert: Whether installation type requires a signed cert.

       - Type: ``boolean``.
       - Default value: ``False``.
       - Additional info: creates a dummy CA to issue public and
         private keys needed for the product to be deployed.

:has_infomodel: Whether the product publishes information about itself.

       - Type: ``boolean``.
       - Default value: ``False``.
       - Additional info: launches
         `QC_INFO_1 <http://egi-qc.github.io/#INFO_MODEL>`_ checks, so
         it's mandatory for the product publishing data (commonly
         through BDII).

:cfgtool: Configuration tool object.

       - Type: ``umd.base.configure.BaseConfig``.
       - Default value: ``None``.
       - Additional info: contains an instance of any class that
         inherits from BaseConfig. Currently available:
         - ``umd.base.configure.YaimConfig``

           :nodetype: YAIM nodetype to be configured.
           :siteinfo: File containing YAIM configuration variables.

         - ``umd.base.configure.PuppetConfig``

           :manifest: Main ".pp" with the configuration to be applied.
           :module_from_puppetforge: list of modules to be installed
                          (from PuppetForge).
           :module_from_repository: module (repotype, repourl) tuples.
           :module_path: Extra Puppet module locations.

:qc_mon_capable: Whether extenal monitoring (aka SAM Nagios) can monitor the
                 product.

       - Type: ``boolean``.
       - Default value: ``False``.

:qc_specific_id: ID that match the list of QC-specific checks to be executed.
                 The check definition must be included in
                 `etc/qc_specific.yaml`.

       - Type: ``str``.
       - Default value: ``None``.

:qc_step: Specific step from the Quality Criteria to run.

       - Type: ``str``, ``list``.
       - Default value: empty list.

:exceptions: Documented exceptions for a given UMD product.

       - Type: ``dict``.
       - Default value: empty dict.

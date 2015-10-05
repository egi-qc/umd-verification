Overview
========


Getting Started
---------------
``umd-verification`` tool uses Python's `Fabric <http://www.fabfile.org/>`_
library.

There is no need to build or install the application, just download the
source code and interact with the tool through `fab` commands.

Note that in order to execute `fab` commands, your current path has to be the
**root path of the repository** i.e. where `fabfile.py` exists.


Basic Usage
-----------

.. _list-cmd-ref:

Listing available deployments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  .. code:: bash

    $ fab -l
    Available commands:

    argus               ARGUS server deployment.
    argus-ees           ARGUS EES daemon deployment.
    bdii-site           Site BDII deployment.
    (..)

Running a deployment
^^^^^^^^^^^^^^^^^^^^

Once selected the most suitable product verification (`commands` in Fabric)
from the command-listing output above, one can trigger the deployment following
the format:

  .. code:: bash

    $ fab <command>:<arg1>=<value1>,<arg2>=<value2>,..

The available runtime arguments are explained in :ref:`runtime-args-ref`
section.


Creating a new verification
---------------------------

`umd/products/` directory contains the `.py` files where all the
available (see :ref:`list-cmd-ref`) deployments are defined.

In order to create a verification for a new product, one has to instantiate
`base.Deploy` class providing a given set of arguments
(see the full list at :ref:`instantiation-args-ref`):

  .. code:: python

    from umd import base

    argus = base.Deploy(
        name="argus",
        doc="ARGUS server deployment.",
        metapkg="emi-argus")

Fabric takes then as available commands every instance of this class found the
product's directory. The command identifier is the value of `name` argument,
while `doc` will contain the description of this command. This is actually the
information displayed when listing commands (see :ref:`list-cmd-ref`).

Note that in the case of adding a new `.py` file under `umd/products`
directory, this new module has to be included in `fabfile.py` in order for
Fabric to find the new command/s. Following the example above, we should add

  .. code:: python

    from umd.products.argus import *

to `fabfile.py` in case that our brand new Python file is called `argus.py`.


.. _test-execution-ref:

Test execution
--------------

After a successful deployment, the last step usually involves testing that the
current deployment actually works. Testing phase corresponds to EGI's
``QC_FUNC_1`` and ``QC_FUNC_2`` steps.

Test definition is placed in `etc/qc_specific.yaml`. The format of each entry
is:

  .. code-block:: yaml

    <id>:
        <qc_func_1|qc_func_2>:
            - test: <path_to_directory_or_executable_file>
              description: <test_description_string>
              user: <user_running_the_executables>
              args: <executable_arguments>

Things to note:

- Tests are included in the `bin/` directory within the repository. The
  currently available tests are described in :ref:`testing-ref`.
- Path (`test` parameter) can either point to a directory or to a particular
  executable file. In the former case all the executable files found in that
  directory will be executed.
- Using `args` only make sense in case of defining file paths (not directory
  paths).
- Environment variables can be passed to the tests at runtime (see
  ``qcenv-*`` argument at :ref:`runtime-args-ref`).

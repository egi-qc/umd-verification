
.. _testing-ref:

Testing
=======

This page documents the tests included with the ``umd-verification`` tool. Note
that the tool allows to execute whatever custom checks located in the system.

`bin/myproxy/client-test.sh`
------------------------------
Retrieves a proxy with VOMS extension from a MyProxy server.

- Accepted arguments: ``retrieve``
- Currently supported VOs: `ops.vo.ibergrid.eu`, `dteam`
- Environment variables needed:

  - ``MYPROXY_SERVER``
  - ``MYPROXY_USER``
  - ``MYPROXY_PASSWD``

  and the optional:

  - ``VO``

  that defaults to ``ops.vo.ibergrid.eu`` VO.

  These variables need to be passed via runtime arguments (as specified in
  :ref:`test-execution-ref`):

  .. code:: bash

    fab ui:qcenv_MYPROXY_SERVER=foo.example.org,qcenv_MYPROXY_USER=bar,qcenv_MYPROXY_PASSWD=baz,..

- Requires a myproxy already stored in ``MYPROXY_SERVER`` with user and
  password credentials:

  .. code:: bash

    echo $MYPROXY_PASSWD | myproxy-init -S -l $MYPROXY_USER -s $MYPROXY_SERVER -m $VO


`bin/srm/client-test.sh`
------------------------

Performs data management checks.

- Accepted arguments:

  - #1 Whether the endpoint is localhost or an external one.

    - Valid values: ``localhost``, ``storm``, ``dpm``, ``dcache``

  - #2 Client to be tested.

    - Valid values: ``lcg-util``, ``dcache-client``, ``gfal2-python``, ``gfal2-util``

- Environment variables:

  - ``SRM_HOST`` *optional*
  - ``SRM_ENDPOINT`` *optional*

  points to the SRM URL following the format `srm://<srm_host>/<srm_vo_path>`

  .. code:: bash

    fab ui:qcenv_SRM_ENDPOINT="srm://srm01.ifca.es:8444/srm/managerv2?SFN=/ops.vo.ibergrid.eu"

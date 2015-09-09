Overview
========


Getting Started
---------------
This tool uses Python's `Fabric <http://www.fabfile.org/>`_ library, just use
`fab` command to make the deployments.


Basic `fab` usage
^^^^^^^^^^^^^^^^^
* To *list* the available UMD product deployments (*commands* term in Fabric):
  .. code:: bash

    # fab -l
    Available commands:

    argus               ARGUS server deployment.
    argus-ees           ARGUS EES daemon deployment.
    bdii-site           Site BDII deployment.
    (..)

* To *run* the deployment:
  .. code:: bash

    # fab argus:installation_type=install,repository_url=..


Therefore the argument passing format works like
``fab <command>:<arg1>=<value1>,<arg2>=<value2>,..<argN>=<valueN>``, where the
available arguments ..

#!/bin/bash -eu

set -x

case $1 in
    glue-validator)
        glue-validator -H localhost -p 2170 -b o=grid -g glue1 -s general -v 3
        ;;
    ldapsearch)
        # FIXME (orviz) Site name is hardcoded
        ldapsearch -xLLL -b mds-vo-name=GRID-SITE,o=grid -p 2170 -h localhost
        ;;
    *)
        echo "No options or option not known"
        exit -1
        ;;
esac

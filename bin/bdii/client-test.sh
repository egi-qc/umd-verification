#!/bin/bash -eu

set -x

case $1 in
    glue-validator)
        glue-validator -H localhost -p 2170 -b o=grid -g glue1 -s general -v 3
        ;;
    ldapsearch)
        # 1. Check whether port 2170 is opened
        max_iterations=10
        iterations=0
        ldap_started=1
        while [ $ldap_started -eq 1 ]; do
            [ -n "`netstat -ln| grep 'LISTEN '| grep 2170`" ] && ldap_started=0
            sleep 2
            iterations=$((iterations+1))
            if [ $iterations -eq $max_iterations ]; then
                echo "Max number of iterations reached. Exiting: port 2170 not opened." && exit 1
            fi
        done

        # 2. Sleep BDII_BREATHE_TIME seconds
        breathe_time=`. /etc/bdii/bdii.conf && echo $BDII_BREATHE_TIME`
        echo "Waiting $breathe_time seconds to check BDII health.."
        sleep $breathe_time

        # 3. 5 attempts to connect to bdii service
        # FIXME (orviz) Site name is hardcoded
        for i in `seq 1 5` ; do 
            ldapsearch -x -h localhost -p 2170 -b mds-vo-name=GRID-SITE,o=grid
            [ $? -eq 0 ] && break
            echo "ldap not started..waiting for 2 seconds.." && sleep 2
        done
        ;;
    *)
        echo "No options or option not known"
        exit -1
        ;;
    esac

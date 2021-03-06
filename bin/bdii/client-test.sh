##!/bin/bash -eu

#set -x
#!/bin/bash

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

case $1 in
    glue-validator)
        glue-validator -H localhost -p 2170 -b o=grid -g glue1 -s general -v 3
        ;;
    ldapsearch-site-bdii)
        site_name=`. /etc/bdii/gip/glite-info-site-defaults.conf && echo $SITE_NAME`
        cmd="ldapsearch -x -h localhost -p 2170 -b mds-vo-name=${site_name},o=grid"
        # 1. Sleep BDII_BREATHE_TIME seconds
        breathe_time=`. /etc/bdii/bdii.conf && echo $BDII_BREATHE_TIME`
        echo "Waiting $breathe_time seconds to check BDII health.."
        sleep $breathe_time

        # 2. 5 attempts to connect to bdii service
        for i in `seq 1 5` ; do 
            set +e
            out=`$cmd 2>&1`
            [ $? -eq 0 ] && >&2 echo $out ; exit 0
            echo "ldap not started..waiting for 2 seconds.." && sleep 2
        done
        ;;
    ldapsearch-top-bdii)
        keep_trying=1
        while [ $keep_trying -eq 1 ]; do
            set +e 
            ldap_proc_num="`ps aux|grep -c \"[l]dapsearch \"`"
            set -e
            if [ $ldap_proc_num -ne "0" ]; then
                echo "Found $ldap_proc_num process running. Sleeping 1 minute.."
                sleep 1m
            else
                sleep 1m
                keep_trying=0
		ldapsearch -x -h localhost -p 2170 -b o=grid
	    fi
        done
        ;;
    ldapsearch-site-bdii-cloud)
        cmd="ldapsearch -x -H ldap://localhost:2170 -b o=glue"

        # 1. Sleep BDII_BREATHE_TIME seconds
        breathe_time=`. /etc/bdii/bdii.conf && echo $BDII_BREATHE_TIME`
        echo "Waiting $breathe_time seconds to check BDII health.."
        sleep $breathe_time

        # 2. 5 attempts to connect to bdii service
        for i in `seq 1 5` ; do 
            set +e
            out=`$cmd 2>&1`
            [ $? -eq 0 ] && >&2 echo $out ; exit 0
            echo "ldap not started..waiting for 2 seconds.." && sleep 2
        done
	# Exit -1 otherwise
        exit -1
        ;;
    *)
        echo "No options or option not known"
        exit -1
        ;;
esac

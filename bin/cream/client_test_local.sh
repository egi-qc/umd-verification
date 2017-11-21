#!/bin/bash

[ $# -eq 1 ] && export X509_USER_PROXY=$1
[ -z $X509_USER_PROXY ] && echo "Proxy not found!" && exit 1

JDL_FILE=/tmp/test_cream.jdl

cat <<EOF > $JDL_FILE
[
executable="/bin/sleep"; 
arguments="60"; 
] 
EOF

whoami
export

jobid=`glite-ce-job-submit -a -r $(hostname -f):8443/cream-slurm-long ${JDL_FILE}`
cream_status=
for i in `seq 1 10` ; do
    cream_status=`glite-ce-job-status $jobid | grep Status | awk -F '[][]' '{print $2}'`
    case $cream_status in
        DONE-OK)
            exit_status=0
            break
            ;;
        DONE-FAILED*|CANCELLED|ABORTED|UNKNOWN)
            exit_status=1
            break
            ;;
        REGISTERED|PENDING|IDLE|*RUNNING)
            sleep 30
            exit_status=2
            ;;
        *)
            exit_status=3
            ;;
    esac
done

echo "Job last status: $cream_status"
exit $exit_status

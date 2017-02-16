#!/bin/bash -eu

set -x

export X509_USER_PROXY=$1
out=`arctest -c \`hostname -f\` -J 1`
jobid=`[[ $out =~ .+(gsiftp://[a-zA-Z0-9\.:/_\-]+) ]] && echo ${BASH_REMATCH[1]}`
arcstat -j $HOME/.arc/jobs.dat
[ -n $jobid ] && echo "Job successfully submitted: $jobid"

#!/bin/bash -eu

## Arguments
##      #1 Name of the jobmanager to use

set -x

[ $# -ne 1 ] && echo -e "Invalid arguments.\n\tUsage: `basename "$0"` <jobmanager name>" && exit 1

TMPDIR=`mktemp -d`
pushd $TMPDIR

echo "Create proxy..."
grid-proxy-init


GRAM_HOST=`hostname`
JOBMANAGER=$1

echo $JOBMANAGER | grep pbs > /dev/null && PARALLEL_JOB=1 || PARALLEL_JOB=0
 
# Simple whoami job
globus-job-run $GRAM_HOST/$JOBMANAGER `which whoami`


# job with file transfer
cat > job1.rsl << EOF
&
(executable=/bin/ls)
(arguments=-l afile)
(file_stage_in = (\$(GLOBUSRUN_GASS_URL) # "$PWD/myfile" afile))
EOF
seq $RANDOM > myfile
globusrun -s -f job1.rsl -r $GRAM_HOST/$JOBMANAGER

# Check job status for longer job
cat > job2.rsl << EOF
&
(executable=/bin/sleep)
(arguments=1m)
EOF
jobid=`globusrun -b -s -f job2.rsl -r $GRAM_HOST/$JOBMANAGER`
status=""
while [ "$status" != "DONE" ]; do
    status=`globusrun -status $jobid`
    sleep 40s
done


# Cancel a running job
cat > job3.rsl << EOF
&
(executable=/bin/sleep)
(arguments=10m)
EOF
jobid=`globusrun -b -s -f job3.rsl -r $GRAM_HOST/$JOBMANAGER`
globusrun -status $jobid
globusrun -k $jobid
globusrun -status $jobid

# Parallel job
if [ "$PARALLEL_JOB" -eq 1 ]; then
    cat > job4.rsl << EOF
&
(executable=/bin/ls)
(arguments=-ltr)
(count=2)
EOF
    globusrun -s -f job4.rsl -r $GRAM_HOST/$JOBMANAGER
fi

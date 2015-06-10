#!/bin/sh

VOMSINFO=`which voms-proxy-info`

PILOT_PROXY=/tmp/x509up_`id -u`
TARGET_USER_PROXY=`pwd`/other.proxy 

export X509_USER_PROXY=$PILOT_PROXY
export GLEXEC_CLIENT_CERT=$TARGET_USER_PROXY
export GLEXEC_SOURCE_PROXY=$TARGET_USER_PROXY

$VOMSINFO -all
/opt/glite/sbin/glexec $VOMSINFO -all

#!/bin/bash -eu

TESTPROXY=`voms-proxy-info -path`

export GLEXEC_CLIENT_CERT=$TESTPROXY
export X509_USER_PROXY=$TESTPROXY

/usr/sbin/glexec /usr/bin/id -a


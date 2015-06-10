#!/bin/sh

export GLEXEC_CLIENT_CERT=$X509_USER_PROXY
export GLEXEC_SOURCE_PROXY=$509_USER_PROXY

/opt/glite/sbin/glexec /usr/bin/id -a ; echo $?

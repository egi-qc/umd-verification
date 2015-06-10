#!/bin/sh

export GLEXEC_CLIENT_CERT=$X509_USER_PROXY

/opt/glite/sbin/glexec /usr/bin/id -a ; echo $?


#!/bin/bash -eu

set -x

echo -e "X509_USER_CERT=/etc/grid-security/hostcert.pem\nX509_USER_KEY=/etc/grid-security/myproxy/hostkey.pem" >> /etc/sysconfig/myproxy-server

#!/bin/bash -eu

set -x

[ ! -d /etc/grid-security/myproxy ] && mkdir /etc/grid-security/myproxy
cp /etc/grid-security/host*.pem /etc/grid-security/myproxy/
chown myproxy:myproxy /etc/grid-security/myproxy/host*.pem
service myproxy-server start

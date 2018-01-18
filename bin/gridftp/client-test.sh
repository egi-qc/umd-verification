#!/bin/bash -eu

set -x

#export X509_USER_PROXY=$1
#
#subject=`sudo voms-proxy-info -acsubject -file $1`
subject="`openssl x509 -in /etc/grid-security/hostcert.pem -noout -subject | sed -e 's/subject= //'`"
the_user=${SUDO_USER:-$USER}
#[ -z "`getent passwd ${the_user}`" ] && sudo useradd -m umd
#sudo chown ${the_user}:${the_user} $1
sudo bash -c "echo \"$subject $the_user\" >> /etc/grid-security/grid-mapfile"

#su $the_user -c "globus-url-copy file:///etc/issue gsiftp://localhost:2811/tmp/issue"
sudo globus-url-copy file:///etc/issue gsiftp://`hostname`:2811/tmp/issue
diff /etc/issue /tmp/issue

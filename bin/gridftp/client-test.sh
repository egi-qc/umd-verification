#!/bin/bash -eu

set -x

export
export X509_USER_PROXY=$1

subject=`sudo voms-proxy-info -acsubject -file $1`
the_user=$SUDO_USER

echo "the user: $SUDO_USER"

sudo chown ${the_user}:${the_user} $1
sudo bash -c "echo \"$subject $the_user\" >> /etc/grid-security/grid-mapfile"

globus-url-copy file:///etc/issue gsiftp://localhost:2811/tmp/issue
diff /etc/issue /tmp/issue

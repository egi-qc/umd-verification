#!/bin/bash -eu

set -x

subject=`voms-proxy-info -acsubject`
sudo bash -c "echo \"$subject $USER\" >> /etc/grid-security/grid-mapfile"

globus-url-copy file:///etc/issue gsiftp://localhost:2811/tmp/issue
diff /etc/issue /tmp/issue

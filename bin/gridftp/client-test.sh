#!/bin/bash -eu

set -x

globus-url-copy file:///etc/issue gsiftp://localhost:2811/tmp/issue
diff /etc/issue /tmp/issue

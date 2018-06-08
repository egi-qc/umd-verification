#!/bin/bash -eu

set -x

PROXY_FILE=$1
PLAYBOOK=/tmp/arc_test.yml

cat <<'EOF' > $PLAYBOOK
---
- hosts: localhost
  roles:
    - role: ansible-arc-test
EOF

sudo ansible-playbook $PLAYBOOK --tags testing --extra-vars "enable_testing=true" --extra-vars "proxy_file=$PROXY_FILE"

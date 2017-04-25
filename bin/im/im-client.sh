#!/bin/bash

cat <<EOF > auth.dat
type = InfrastructureManager; username = IMusername; password = IMpassword
EOF

im_client.py -a auth.dat list

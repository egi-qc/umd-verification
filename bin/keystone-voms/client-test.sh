#!/bin/bash

if [ "`voms-proxy-info --all 2>/dev/null | grep type | grep RFC`" ]; then
    echo "No valid RFC proxy found. Exiting.."
    exit -1
fi

curl --cert $X509_USER_PROXY  -d '{"auth":{"voms": true}}' \
    -H "Content-type: application/json" \
    https://`hostname -f`:5000/v2.0/tokens

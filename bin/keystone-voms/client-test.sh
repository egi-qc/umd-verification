#!/bin/bash


[ $# -eq 1 ] && export X509_USER_PROXY=$1
[ -z $X509_USER_PROXY ] && echo "Proxy not found!" && exit 1

if [ -z "`voms-proxy-info --all -file $X509_USER_PROXY 2>/dev/null | grep type | grep RFC`" ]; then
    echo "No valid RFC proxy found. Exiting.."
    exit -1
fi

function get_token_id {
    echo `curl --silent --cert $X509_USER_PROXY -d '{"auth":{"voms": true}}' -H "Content-type: application/json" https://$(hostname -f):5000/v2.0/tokens | python -c "import sys, json; print json.load(sys.stdin)[u'access'][u'token'][u'id']"`
}

function get_tenant_name {
    # 1st tenant
    echo `curl --silent -H "X-Auth-Token:$1" https://$(hostname -f):5000/v2.0/tenants | python -c "import sys, json; print json.load(sys.stdin)[u'tenants'][0][u'name']"`
}

function get_scoped_token_id {
    echo `curl --silent --cert $X509_USER_PROXY -H 'Content-Type: application/json' -d '{"auth": {"voms": true, "tenantName": "'"$1"'"}}' https://$(hostname -f):5000/v2.0/tokens | python -c "import sys, json; print json.load(sys.stdin)[u'access'][u'token'][u'id']"`
}

TID=$(get_token_id)
TENANT=$(get_tenant_name $TID)
get_scoped_token_id $TENANT

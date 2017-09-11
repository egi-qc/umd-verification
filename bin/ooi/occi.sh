. ${1}/openrc

export KID=`curl -i -s -H "Content-Type: application/json" -d '{"auth":{"identity":{"methods":["password"],"password":{"user":{"name":"demo","domain":{"id":"default"},"password":"secret"}}},"scope":{"project":{"name":"demo","domain":{"id":"default"}}}}}' ${OS_AUTH_URL}/v3/auth/tokens | grep "X-Subject-Token" | awk '{print $2}'`
echo $KID
#curl -v -H 'X-Auth-Token: '$KID -X GET localhost:8787/occi1.1/-/

#!/bin/bash

cat > /var/www/html/test.html <<EOF
<html><body><h1>Hello Grid</h1></body></html>
EOF

cat >/var/www/html/.gacl <<EOF
<gacl>
  <entry>
    <any-user/>
      <allow><read/></allow>
  </entry>
</gacl>
EOF

curl -k --cert .x509up_u7036 --key .x509up_u7036 --capath /etc/grid-security/certificates https://localhost/test.html
[ $? -ne 0 ] && curl -k http://localhost/test.html

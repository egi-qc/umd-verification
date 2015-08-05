#!/bin/bash

set -x

# Configuration
host=0.0.0.0
port=6217

MSG='<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:dsig="http://www.w3.org/2000/09/xmldsig#" xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:XACMLcontext="urn:oasis:names:tc:xacml:2.0:context:schema:os" xmlns:XACMLassertion="urn:oasis:names:tc:xacml:2.0:profile:saml2.0:v2:schema:assertion" xmlns:XACMLpolicy="urn:oasis:names:tc:xacml:2.0:policy:schema:os" xmlns:xenc="http://www.w3.org/2001/04/xmlenc#" xmlns:XACMLService="http://www.globus.org/security/XACMLAuthorization/bindings" xmlns:XACMLsamlp="urn:oasis:names:tc:xacml:2.0:profile:saml2.0:v2:schema:protocol" xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">
<SOAP-ENV:Body>
<XACMLsamlp:XACMLAuthzDecisionQuery CombinePolicies="true" ReturnContext="true" InputContextOnly="false" IssueInstant="2010-03-25T14:55:01Z" Version="2.0" ID="ID-1804289383">
<saml:Issuer xsi:type="saml:NameIDType" Format="urn:oasis:names:tc:SAML:1.1:nameid-format:X509SubjectName">NetCat</saml:Issuer>
<XACMLcontext:Request xsi:type="XACMLcontext:RequestType">
<XACMLcontext:Action xsi:type="XACMLcontext:ActionType">
</XACMLcontext:Action>
</XACMLcontext:Request>
</XACMLsamlp:XACMLAuthzDecisionQuery>
</SOAP-ENV:Body>
</SOAP-ENV:Envelope>
'

# Takes three args, a test string and a pattern to match to
test_main() {
  output=`echo -n "$1" | nc -n -i1 $host $port | grep -w "$2"`
  if [ -z "$output" ]
  then
    echo "ERR"
  else
    echo "OK"
  fi  
}

echo -en "Basic sanity test\t"
test_main "$MSG" "200 OK"
echo -en "Basic failure test\t"
test_main "<TEST>" "500 Internal"


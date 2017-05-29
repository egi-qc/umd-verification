#!/usr/bin/env python

import argparse
import os
import socket

import novaclient
import novaclient.auth_plugin
import novaclient.client
import novaclient.exceptions


parser = argparse.ArgumentParser(description='Get keystone auth token.')
parser.add_argument("tenant", metavar="TENANT|VO", type=str,
                    help="Tenant mapping the VO")
parser.add_argument("--proxy-path", metavar="PATH", type=str,
                    help="Path where the proxy is stored")
args = parser.parse_args()


username = password = None
tenant = args.tenant
url = "https://%s:5000/v2.0/" % socket.getfqdn()
version = 2

auth_system = "voms"
novaclient.auth_plugin.discover_auth_systems()
auth_plugin = novaclient.auth_plugin.load_plugin(auth_system)
if args.proxy_path:
    auth_plugin.opts["x509_user_proxy"] = args.proxy_path
else:
    auth_plugin.opts["x509_user_proxy"] = os.environ["X509_USER_PROXY"]

client = novaclient.client.Client(version, username, password,
                                  tenant, url,
                                  cacert="/etc/grid-security/certificates/0d2a3bdd.0",
                                  #insecure=True,
                                  auth_plugin=auth_plugin,
                                  auth_system=auth_system)
try:
    client.authenticate()
except novaclient.exceptions.EndpointNotFound:
    pass

print("Token retrieved from proxy: %s" % client.client.auth_token)

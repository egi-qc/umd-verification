#!/usr/bin/env python

import os

import novaclient
import novaclient.auth_plugin
import novaclient.client

username = password = None
tenant = "VO:dteam"
url = "https://ubuntu-keystonevoms.privatevlan.cloud.ifca.es:5000/v2.0/"
version = 2

auth_system = "voms"
novaclient.auth_plugin.discover_auth_systems()
auth_plugin = novaclient.auth_plugin.load_plugin(auth_system)
auth_plugin.opts["x509_user_proxy"] = os.environ["X509_USER_PROXY"]

client = novaclient.client.Client(version, username, password,
                                    tenant, url,
                                    auth_plugin=auth_plugin,
                                    auth_system=auth_system,
                                    insecure=True)
#print dir(client)
#print client.__dict__

print(client.servers.list())
#print os.environ["X509_USER_PROXY"]

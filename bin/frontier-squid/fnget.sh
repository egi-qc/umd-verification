#!/bin/bash

#set -x

export http_proxy=http://localhost:3128

fnget_py="/tmp/fnget.py"
wget http://frontier.cern.ch/dist/fnget.py -O $fnget_py
chmod +x $fnget_py

$fnget_py --url=http://cmsfrontier.cern.ch:8000/FrontierProd/Frontier --sql="select 1 from dual"
$fnget_py --url=http://cmsfrontier.cern.ch:8000/FrontierProd/Frontier --sql="select 1 from dual"
tail -1 /var/log/squid/access.log | grep TCP_MEM_HIT
echo $?

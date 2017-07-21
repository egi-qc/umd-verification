#!/bin/bash

# Args:
#   $1: configuration management tool (ansible, puppet)
#   $2: Role/module URL 

## sudo OR rvmsudo
[[ $OS == sl6* ]] && sudocmd=rvmsudo || sudocmd=sudo

## ansible OR puppet
case $1 in
    *ansible*)
        $sudocmd pip install ansible==2.2
        git clone $2 /tmp && sudo ansible-galaxy install -r `basename ${2}`/requirements.yml
        ;;
    #*puppet*)
    #    ;;
    *)
        echo "Configuration management tool '$1' not supported" && exit -1
        ;;
esac

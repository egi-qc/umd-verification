#!/bin/bash

# Args:
#   $1: configuration management tool (ansible, puppet)
#   $2: Role/module URL 

module_name="`basename $2`"

## sudo OR rvmsudo
[[ $OS == sl6* ]] && sudocmd=rvmsudo || sudocmd=sudo

## ansible OR puppet
case $1 in
    *ansible*)
        $sudocmd pip install ansible==2.2
        module_path=/tmp/$module_name
        git clone $2 $module_path && sudo ansible-galaxy install -r ${module_path}/requirements.yml
        ;;
    #*puppet*)
    #    ;;
    *)
        echo "Configuration management tool '$1' not supported" && exit -1
        ;;
esac

# fab execution
Verification_repository=$(./bin/jenkins/parse_multiline.sh ${Verification_repository})
$sudocmd fab argus:umd_release=${UMD_release},${Verification_repository},log_path=logs

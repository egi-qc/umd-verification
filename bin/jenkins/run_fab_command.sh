#!/bin/bash

# Args:
#   $1: distribution and release (umd3, umd4, cmd1)
#   $2: configuration management tool (ansible, puppet)
#   $3: Role/module URL
#   $4: verification repository/s 

distro=$1
config_tool=$2
module_name="`basename $3`"
verification_repos=$4

## sudo OR rvmsudo
[[ $OS == sl6* ]] && sudocmd=rvmsudo || sudocmd=sudo

## ansible OR puppet
case $config_tool in
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

# UMD or CMD
case $distro in
    umd3) release_str="umd_release=3" ;;
    umd4) release_str="umd_release=4" ;;
    cmd1) release_str="cmd_release=1" ;;
    *) echo "UMD distribution '$distro' not known" && exit -1
esac

# fab execution
if [ -n "${verification_repos}" ] ; then
    verification_repos=$(./bin/jenkins/parse_multiline.sh ${verification_repos})
    $sudocmd fab argus:${release_str},${Verification_repository},log_path=logs
else
    $sudocmd fab argus:${release_str},log_path=logs
fi

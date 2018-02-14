get_umd_release () {
    # $1 - UMD/CMD distribution: umd3,umd4,cmd1 

    # UMD or CMD
    case $1 in
        UMD3) release_str="umd_release=3" ;;
        UMD4) release_str="umd_release=4" ;;
        CMD1|CMD-OS-1) release_str="cmd_release=1,openstack_release=mitaka" ;;
        CMD-ONE-1) release_str="cmd_one_release=1" ;;
        *) echo "UMD distribution '$distro' not known" && exit -1
    esac

    echo $release_str
}


get_sudo_type () {
    # $1 - Operating system: sl6, (others)

    # Latest image is CentOS6
    if [[ $1 == *sl6* ]]; then
        sudocmd=rvmsudo
        . ~/.rvm/environments/default
    else
        sudocmd=sudo
    fi

    echo $sudocmd
}


multiple_arg () {
    # $1 - Prefix
    # $2 - Arguments
    prefix=$1
    shift

    c=0
    repostr=''
    for i in "$@"; do
        c=$((c+1))
        [ -n "$repostr" ] && repostr=$repostr','
        repostr=$repostr"${prefix}_$c=$i"
    done
    
    echo $repostr
}


get_repos () {
    # $1 - Comma-separated string with the repository URLs
    
    prefix=repository_file
    multiple_arg $prefix $@
}


get_packages () {
    # $1 - Comma-separated string with the package/s
    
    prefix=package
    multiple_arg $prefix $@
}


deploy_config_management () {
    # $1 - config management tool: ansible, puppet
    # $2 - sudo type
    # $3 - module URL

    sudocmd=$2
    ## ansible OR puppet
    case $1 in
        *ansible*)
            module_url=$3
            module_name="`basename $3`"
            module_path=/tmp/$module_name
            $sudocmd pip install ansible==2.2
            $sudocmd rm -rf $module_path
            git clone $module_url $module_path
            $sudocmd ansible-galaxy install -r ${module_path}/requirements.yml
            ;;
        *puppet*)
            #if [[ $OS == sl6* ]] ; then 
            #    $sudocmd /usr/local/rvm/rubies/ruby-1.9.3-p551/bin/gem install librarian-puppet
            #    $sudocmd sed -i '/secure_path =/ s/$/:\/usr\/local\/rvm\/gems\/ruby-1.9.3-p551\/bin/' /etc/sudoers
            #fi
            ;;
        *)
            echo "Configuration management tool '$1' not supported" && exit -1
            ;;
    esac
}

add_hostname_as_localhost () {
    # $1 - sudo type

    # Set a system's FQDN hostname
    MY_DOMAIN=egi.ifca.es
    [[ "`hostname -f`" != *"$MY_DOMAIN" ]] && $1 hostname "`hostname`.${MY_DOMAIN}"
    # Append it to /etc/hosts
    #$1 sed -i "/^127\.0\.0\.1/ s/$/ `hostname`/" /etc/hosts
    $1 sed -i "/^127\.0\.0\.1/ s/ localhost/ `hostname`/" /etc/hosts
}

deploy_devstack () {
    devstack_home=${HOME}/devstack
    lastpath=`pwd`
    git clone https://github.com/openstack-dev/devstack $devstack_home
    cd $devstack_home
    cat <<EOF > ${devstack_home}/local.conf
[[local|localrc]]
ADMIN_PASSWORD=secret
DATABASE_PASSWORD=secret
RABBIT_PASSWORD=secret
SERVICE_PASSWORD=secret
disable_service n-net
enable_service q-svc
enable_service q-agt
enable_service q-dhcp
enable_service q-l3
enable_service q-meta
IP_VERSION=4
NEUTRON_CREATE_INITIAL_NETWORKS=False
#FLOATING_RANGE=192.168.1.224/27
#FIXED_RANGE=10.11.12.0/24
#FIXED_NETWORK_SIZE=256
#FLAT_INTERFACE=eth0
EOF
    ./stack.sh || sudo systemctl restart "devstack@*" # FIXME(orviz) remove this part whenever devstack stops failing in Ubuntu 16.04
    if sudo ls /etc/apt/sources.list.d/*ocata*.list 1> /dev/null 2>&1 ; then sudo rm -f /etc/apt/sources.list.d/*ocata*.list ; fi # FIXME(orviz) devstack add this repository file
     cd $lastpath
     echo $devstack_home
}

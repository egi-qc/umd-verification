WORKSPACE_CONFIG_DIR="`pwd`/_files"

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


get_product_version () {
    SUBSTR=`echo $URL | grep -Po '(?<=unverified\/).*\/\d'`
    echo `sed '0,/\// s//-/' <<<$SUBSTR | tr '/' '.'`
}

get_cmt_module () {
    # $1 - fab command, as it appears in `fab -l`
    # $2 - config management tool: ansible, puppet

    FAB_CMD=$1
    TOOL=$2
    PARENT_MODULE=
    case $FAB_CMD in
        bdii*) PARENT_MODULE=bdii ; INSTANCE=bdii_site ;;
        cloud-info-provider*) PARENT_MODULE=cloud_info_provider ; INSTANCE=cloud_info_provider;;
        clients-solo*) PARENT_MODULE=clients_solo ; INSTANCE=clients_solo ;;
        frontier-squid*) PARENT_MODULE=frontier_squid; INSTANCE=frontier_squid ;;
        keystone-voms*) PARENT_MODULE=keystone_voms; INSTANCE=keystone_voms ;;
        individual-packages*) PARENT_MODULE=individual_packages; INSTANCE=individual_packages ;;
        release-candidate*) PARENT_MODULE=rc; INSTANCE=rc ;;
        *) PARENT_MODULE=$FAB_CMD ; INSTANCE=$FAB_CMD;;
    esac
    
    ATTR=
    if [ $TOOL == "puppet" ]; then
        ATTR="manifest"
    elif [ $TOOL == "ansible" ]; then
        ATTR="role"
    fi

    echo "`python -c "from umd.products import $PARENT_MODULE ; print ${PARENT_MODULE}.${INSTANCE}.cfgtool.${ATTR}"`"
}

generate_readme () {
    # $1 - fab command, as it appears in `fab -l`
    # $2 - config management tool: ansible, puppet
    # $3 - operating system
    # $4 - Jenkins build URL
    # $5 - Verification repository

    FAB_CMD=$1
    TOOL=$2
    OS=$3
    BUILD_URL=$4
    VERIFICATION_REPO=$5

    ! [ -d $WORKSPACE_CONFIG_DIR ] && mkdir $WORKSPACE_CONFIG_DIR
    README=${WORKSPACE_CONFIG_DIR}/README.md

    MODULE=$(get_cmt_module $FAB_CMD $TOOL)
    MODULE_BASENAME=`basename $MODULE`

    if [ $2 == "puppet" ]; then
cat > $README <<EOF
## Directory structure

    |-- Puppetfile
    |-- puppet
        |-- hiera.yaml
        |-- hieradata
            |-- umd.yaml
            |-- extra_vars.yaml
        |-- manifests
            |-- $MODULE

## Hiera variables

Do not rely on the values set for the variables in the Hiera YAML files 
within \`puppet/hieradata/\`; set here the right values that work for your
environment.

## Deployment with \`puppet apply\`

    $ git clone https://github.com/egi-qc/deployment-howtos && cd deployment-howtos/${FAB_CMD}/${OS}
    
    $ librarian-puppet install --clean --path=/etc/puppet/modules --verbose
    
    $ cp puppet/hiera.yaml /etc/puppet/hiera.yaml
    $ cp -r puppet/hieradata /etc/puppet/hieradata
    
    $ puppet apply --modulepath /etc/puppet/modules manifests/`basename $MODULE`

Please note:
  - _Use \`sudo\` with non-root accounts_
  - \`librarian-puppet\` is only needed for deploying the module dependencies. If you
    have installed them manually, ignore this step.

`[ -n "$VERIFICATION_REPO" ] && echo Product version: $(get_product_version $VERIFICATION_REPO)`
Jenkins build URL: $BUILD_URL
EOF
    elif [ $2 == "ansible" ]; then
        if [[ $MODULE = *"https"* ]]; then
cat >> $README <<EOF
## Directory structure

    |-- vars
        |-- umd.yaml
        |-- extra_vars.yaml

## Variables

Do not rely on the values set for the variables in the YAML files; set here 
the right values that work for your environment.

## Deployment with \`ansible-pull\`

    $ git clone $MODULE /tmp/$MODULE_BASENAME

    $ ansible-galaxy install -p /etc/ansible/roles -r /tmp/${MODULE_BASENAME}/requirements.yml

    $ ansible-pull -vvv -C master -d /etc/ansible/roles/${MODULE_BASENAME} -i /etc/ansible/roles/${MODULE_BASENAME}/hosts -U $MODULE --extra-vars '@vars/umd.yaml' --extra-vars '@vars/extra_vars.yaml' --tags 'all'

Please note:
  - _Use \`sudo\` with non-root accounts_

Jenkins build URL: $BUILD_URL
EOF
        else
cat >> $README <<EOF
    GUIDELINES NOT AVAILABLE        
EOF
        fi
    fi
}


archive_artifacts_in_workspace() {
    # $1 - fab command, as it appears in `fab -l`
    # $2 - config management tool: ansible, puppet
    # $3 - operating system
    # $4 - Jenkins build URL
    # $5 - Verification repository (optional)

    FAB_CMD=$1
    TOOL=$2

    ! [ -d $WORKSPACE_CONFIG_DIR ] && mkdir $WORKSPACE_CONFIG_DIR
    
    if [ $2 == "puppet" ]; then
        MODULE=$(get_cmt_module $FAB_CMD $TOOL)
        cp /tmp/Puppetfile $WORKSPACE_CONFIG_DIR/
        mkdir $WORKSPACE_CONFIG_DIR/puppet
        cp -r /etc/puppet/hiera.yaml /etc/puppet/hieradata $WORKSPACE_CONFIG_DIR/puppet
	mkdir $WORKSPACE_CONFIG_DIR/puppet/manifest 
        cp etc/puppet/${MODULE} $WORKSPACE_CONFIG_DIR/puppet/manifest
    elif [ $2 == "ansible" ]; then
        mkdir $WORKSPACE_CONFIG_DIR/vars
        cp /tmp/*.yaml $WORKSPACE_CONFIG_DIR/vars/
    fi

    generate_readme $@
}

publish_howtos () {
    # $1 - fab command, as it appears in `fab -l`
    # $2 - operating system
    # $3 - Jenkins build URL

    FAB_CMD=$1
    OS=$2
    BUILD_URL=$3

    git config --global user.name "Pablo Orviz"
    git config --global user.email orviz@ifca.unican.es
    wget --no-check-certificate https://gist.githubusercontent.com/dadrian/bad309f16e407526741e/raw/462e7ef24387948e17e68a3975b057200fc05533/known_hosts -O ~/.ssh/known_hosts
    #echo "github.com,192.30.253.112 ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ==" >> ~/.ssh/known_hosts
    ssh -T git@github.com || echo

    workspace=`pwd`
    git clone https://github.com/egi-qc/deployment-howtos /tmp/deployment-howtos && cd /tmp/deployment-howtos
    git remote set-url origin git@github.com:egi-qc/deployment-howtos.git
    ! [ -d ${FAB_CMD}/${OS} ] && mkdir -p ${FAB_CMD}/${OS}
    cp -r ${WORKSPACE_CONFIG_DIR}/* ${FAB_CMD}/${OS}/
    git add ${FAB_CMD}/${OS}/
    git commit -a -m "${FAB_CMD}/${OS}/ deployment how-to (build $BUILD_URL)"
    git push origin master
    cd $workspace
}

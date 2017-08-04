function get_umd_release {
    # $1 - UMD/CMD distribution: umd3,umd4,cmd1 

    # UMD or CMD
    case $1 in
        umd3) release_str="umd_release=3" ;;
        umd4) release_str="umd_release=4" ;;
        cmd1) release_str="cmd_release=1" ;;
        *) echo "UMD distribution '$distro' not known" && exit -1
    esac

    echo $release_str
}


function get_sudo_type {
    # $1 - Operating system: sl6, (others)

    [[ $OS == sl6* ]] && sudocmd=rvmsudo || sudocmd=sudo
    
    echo $sudocmd
}


function get_repos {
    # $1 - Comma-separated string with the repository URLs
    # $2 - Argument name (prefix)
    
    #prefix=$1
    #shift
    prefix=repository_file
    
    c=0
    repostr=''
    for i in "$@"; do
        c=$((c+1))
        [ -n "$repostr" ] && repostr=$repostr','
        repostr=$repostr"${prefix}_$c=$i"
    done
    
    echo $repostr
}


function deploy_config_management {
    # $1 - config management tool: ansible, puppet
    # $2 - sudo type
    # $3 - module URL

    module_url=$3
    module_name="`basename $3`"
    ## ansible OR puppet
    case $1 in
        *ansible*)
            $2 pip install ansible==2.2
            module_path=/tmp/$module_name
            $2 rm -rf $module_path
            git clone $module_url $module_path
            $2 ansible-galaxy install -r ${module_path}/requirements.yml
            ;;
        #*puppet*)
        #    ;;
        *)
            echo "Configuration management tool '$1' not supported" && exit -1
            ;;
    esac
}

get_repos repository_file http://admin-repo.egi.eu/sw/unverified/umd-4.infn.argus.centos7.x86_64/1/7/3/repofiles/INFN.argus.centos7.x86_64.repo

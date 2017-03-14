[[ $1 == sl6* ]] && sudocmd=rvmsudo || sudocmd=sudo

$sudocmd pip install -r requirements.txt

[ -z "$UMD_release" ] && UMD_release=4
fabcmd="$sudocmd fab fts:umd_release=${UMD_release},log_path=logs"

Verification_repository=$(./bin/jenkins/parse_repos.sh ${Verification_repository})
[ -n "$Verification_repository" ] && fabcmd=${fabcmd},${Verification_repository}

[ "${Deployment_type}" == "installation-only" ] && fabcmd="${fabcmd},qc_step=QC_DIST_1"

set +e
$fabcmd
# very*20 dirty hack
[[ $OS == centos* ]] && repeat=1 || repeat=0
[[ $repeat -eq 1 ]] && $fabcmd,dont_ask_cert_renewal=True

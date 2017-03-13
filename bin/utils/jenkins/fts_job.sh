[[ $OS == sl6* ]] && sudocmd=rvmsudo || sudocmd=sudo

$sudocmd pip install -r requirements.txt

Verification_repository=$(./bin/jenkins/parse_repos.sh ${Verification_repository})

if [ "${Deployment_type}" == "installation-only" ]; then
    fabcmd="$sudocmd fab fts:umd_release=${UMD_release},${Verification_repository},log_path=logs,qc_step=QC_DIST_1"
else
    fabcmd="$sudocmd fab fts:umd_release=${UMD_release},${Verification_repository},log_path=logs"
fi

set +e
$fabcmd
# very*20 dirty hack
[[ $OS == centos* ]] && repeat=1 || repeat=0
[[ $repeat -eq 1 ]] && $fabcmd,dont_ask_cert_renewal=True

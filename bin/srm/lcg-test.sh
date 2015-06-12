#!/bin/bash -eu

## Arguments 
##      #1 Whether the endpoint is localhost or an external one.
##          - Valid values: localhost, storm, dpm, dcache

[ $# -ne 1 ] && echo -e "Invalid arguments.\n\tUsage: `basename "$0"` [localhost|storm|dpm|dcache]" && exit 1

VO=`voms-proxy-info -vo`
case $1 in
    localhost) 
        SE_HOST=`hostname -f`
        ;;
    # FIXME(orviz) hardcoded values!
    storm) 
        SE_HOST=srm01.ncg.ingrid.pt 
	SRM_BASE="srm://$SE_HOST:8444/srm/managerv2?SFN=/ibergrid/ops"
        ;;
    dpm)
        SE_HOST=lcg-srm.ecm.ub.es 
        SRM_BASE="srm://$SE_HOST/dpm/ecm.ub.es/home/ops.vo.ibergrid.eu"
        ;;
    dcache) 
        SE_HOST=srm.ciemat.es
        SRM_BASE="srm:/$SE_HOST//pnfs/ciemat.es/data/iberops"
        ;;
    *)
        echo "Not a valid tag for an SRM endpoint: $1" && exit 1
        ;;
esac


# this may not be true for non StoRM, is there any 
# easy way to check this

#export LCG_GFAL_INFOSYS=$SE_HOST:2170

FILE=`mktemp`
FILE2=`mktemp`

echo > $FILE << EOF
Hello world!
$RANDOM
$RANDOM
$RANDOM
EOF

REMOTE_FILE=test_`date +%s`

export LCG_GFAL_INFOSYS=topbdii.core.ibergrid.eu:2170

set -x
lcg-ls -vl $SRM_BASE

lcg-cp -D srmv2 -v file:$FILE $SRM_BASE/$REMOTE_FILE

lcg-gt -T srmv2 -v $SRM_BASE/$REMOTE_FILE gsiftp 

lcg-gt -T srmv2 -v $SRM_BASE/$REMOTE_FILE https

lcg-gt -T srmv2 -v $SRM_BASE/$REMOTE_FILE file

lcg-ls -vl $SRM_BASE | grep $REMOTE_FILE 

lcg-cp -T srmv2 -v $SRM_BASE/$REMOTE_FILE file:$FILE2

diff $FILE $FILE2

lcg-del -b -T srmv2 -vl $SRM_BASE/$REMOTE_FILE

set +x
echo "Tests succeded!"
rm -rf $FILE
rm -rf $FILE2

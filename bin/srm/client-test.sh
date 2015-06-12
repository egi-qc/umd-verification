#!/bin/bash -eu

## Arguments 
##      #1 Whether the endpoint is localhost or an external one.
##          - Valid values: localhost, storm, dpm, dcache
##      #2 Client to be tested.
##          - Valid values: lcg-util, dcache-client

[ $# -ne 2 ] && echo -e "Invalid arguments.\n\tUsage: `basename "$0"` [localhost|storm|dpm|dcache] [lcg-util|dcache-client|gfal2-python|gfal2-util]" && exit 1

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
        SRM_BASE="srm://$SE_HOST:8443/srm/managerv2?SFN=//pnfs/ciemat.es/data/iberops"
        ;;
    *)
        echo "Not a valid tag for an SRM endpoint: $1" && exit 1
        ;;
esac

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
set -e

case $2 in
    lcg-util)
        lcg-ls -vl $SRM_BASE
        lcg-cp -D srmv2 -v file:$FILE $SRM_BASE/$REMOTE_FILE
        lcg-gt -T srmv2 -v $SRM_BASE/$REMOTE_FILE gsiftp 
        lcg-gt -T srmv2 -v $SRM_BASE/$REMOTE_FILE https
        lcg-gt -T srmv2 -v $SRM_BASE/$REMOTE_FILE file
        lcg-ls -vl $SRM_BASE | grep $REMOTE_FILE 
        lcg-cp -T srmv2 -v $SRM_BASE/$REMOTE_FILE file:$FILE2
        diff $FILE $FILE2
        lcg-del -b -T srmv2 -vl $SRM_BASE/$REMOTE_FILE
        ;;
    dcache-client)
        srmping -retry_num=2 -retry_timeout=10 -2 $SRM_BASE
        srmls -retry_num=2 -retry_timeout=10 -2 $SRM_BASE
        srmcp -retry_num=2 -retry_timeout=10 -2 file:///$FILE $SRM_BASE/$REMOTE_FILE
        srmls -retry_num=2 -retry_timeout=10 -2 $SRM_BASE | grep $REMOTE_FILE
        #srmcp -retry_num=2 -retry_timeout=10 -2 $SRM_BASE/$REMOTE_FILE file:///$FILE2
        #diff $FILE $FILE2
        srmrm -retry_num=2 -retry_timeout=10 -2 $SRM_BASE/$REMOTE_FILE
        ;;
    gfal2-util)
        gfal-ls $SRM_BASE
        gfal-copy file:$FILE $SRM_BASE/$REMOTE_FILE
        gfal-ls $SRM_BASE/$REMOTE_FILE
        gfal-cat $SRM_BASE/$REMOTE_FILE
        rm -f $FILE2
        gfal-copy $SRM_BASE/$REMOTE_FILE file:$FILE2
        diff $FILE $FILE2
        gfal-rm $SRM_BASE/$REMOTE_FILE
        ;;
    gfal2-python)
        python bin/srm/gfal2/gfal2_simple_listing.py $SRM_BASE
        python bin/srm/gfal2/gfal2_long_listing.py $SRM_BASE
        python bin/srm/gfal2/gfal2_copy.py file:$FILE $SRM_BASE/$REMOTE_FILE
        python bin/srm/gfal2/gfal2_bring_online.py $SRM_BASE/$REMOTE_FILE
        python bin/srm/gfal2/gfal2_get_turls.py $SRM_BASE/$REMOTE_FILE
        #python bin/srm/gfal2/gfal2_python_read.py $SRM_BASE
        ;;
    *)
        echo "Not a supported client: $2" && exit 1
esac

set +x
set +e 

echo "Tests succeded!"
rm -f $FILE
rm -f $FILE2

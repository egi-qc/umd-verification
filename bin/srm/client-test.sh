#!/bin/bash -eu

## Arguments 
##      #1 Whether the endpoint is localhost or an external one.
##          - Valid values: localhost, storm, dpm, dcache
##      #2 Client to be tested.
##          - Valid values: lcg-util, dcache-client, gfal2-python, gfal2-util

export BDII_HOST=topbdii.core.ibergrid.eu
#: ${LCG_GFAL_INFOSYS:=topbdii.core.ibergrid.eu:2170}
#export LCG_GFAL_INFOSYS

: ${SRM_PORT:=8444}

function get_vo_path {
    # Arguments
    #   #1 SRM hostname
    #   #2 VO name
    VO_PATH=`ldapsearch -LLL -x -h $BDII_HOST -p 2170 -b o=grid  "(|(&(GlueChunkKey=GlueSEUniqueID=$1)(|(GlueSAAccessControlBaseRule=$2)(GlueSAAccessControlBaseRule=VO:$2)))(&(GlueChunkKey=GlueSEUniqueID=$1)(|(GlueVOInfoAccessControlBaseRule=$2)(GlueVOInfoAccessControlBaseRule=VO:$2))) (&(GlueServiceUniqueID=*://%s*)(GlueServiceVersion=2.*)(GlueServiceType=srm*)))" GlueVOInfoPath | grep GlueVOInfoPath`
    VO_PATH=${VO_PATH#*: }
    echo $VO_PATH
}


[ $# -ne 2 ] && echo -e "Invalid arguments.\n\tUsage: `basename "$0"` [localhost|storm|dpm|dcache] [lcg-util|dcache-client|gfal2-python|gfal2-util]" && exit 1

VO=`voms-proxy-info -vo`
EXTRA_OPTS=

case $1 in
    localhost)
        SRM_HOST=`hostname -f`
        BDII_HOST=$SRM_HOST
        VO_PATH=$(get_vo_path $SRM_HOST $VO)
	    SRM_ENDPOINT="srm://${SRM_HOST}:${SRM_PORT}/srm/managerv2?SFN=/${VO_PATH}"
	    EXTRA_OPTS="-b"
        ;;
    storm) 
        : ${SRM_HOST:=srm01.ncg.ingrid.pt}
        VO_PATH=$(get_vo_path $SRM_HOST $VO)
        : ${SRM_ENDPOINT:="srm://${SRM_HOST}:8444/srm/managerv2?SFN=${VO_PATH}"}
        ;;
    dpm)
        : ${SRM_HOST:=lcg-srm.ecm.ub.es}
        VO_PATH=$(get_vo_path $SRM_HOST $VO)
        : ${SRM_ENDPOINT:="srm://${SRM_HOST}/${VO_PATH}"}
        ;;
    dcache) 
        : ${SRM_HOST:=srm.ciemat.es}
        VO_PATH=$(get_vo_path $SRM_HOST $VO)
        : ${SRM_ENDPOINT:="srm://${SRM_HOST}:8443/srm/managerv2?SFN=/${VO_PATH}"}
        ;;
    *)
        echo "Not a valid tag for an SRM endpoint: $1" && exit 1
        ;;
esac

echo "== Summary =="
echo -e "\t* Type of SRM endpoint: $1"
echo -e "\t* Client to be tested: $2"
echo -e "\t* SRM endpoint: $SRM_ENDPOINT"

FILE=`mktemp`
FILE2=`mktemp`

echo > $FILE << EOF
Hello world!
$RANDOM
$RANDOM
$RANDOM
EOF

REMOTE_FILE=test_`date +%s`

set -x
set -e

case $2 in
    lcg-util)
        lcg-ls $EXTRA_OPTS -D srmv2 -vl $SRM_ENDPOINT
        lcg-cp $EXTRA_OPTS -D srmv2 -v file:$FILE $SRM_ENDPOINT/$REMOTE_FILE
        lcg-gt $EXTRA_OPTS -T srmv2 -v $SRM_ENDPOINT/$REMOTE_FILE gsiftp 
        lcg-gt $EXTRA_OPTS -T srmv2 -v $SRM_ENDPOINT/$REMOTE_FILE https
        lcg-gt $EXTRA_OPTS -T srmv2 -v $SRM_ENDPOINT/$REMOTE_FILE file
        lcg-ls $EXTRA_OPTS -D srmv2 -vl $SRM_ENDPOINT | grep $REMOTE_FILE 
        lcg-cp $EXTRA_OPTS -T srmv2 -v $SRM_ENDPOINT/$REMOTE_FILE file:$FILE2
        diff $FILE $FILE2
        lcg-del $EXTRA_OPTS -T srmv2 -vl $SRM_ENDPOINT/$REMOTE_FILE
        ;;
    dcache-client)
        srmping -retry_num=2 -retry_timeout=10 -2 $SRM_ENDPOINT
        srmls -retry_num=2 -retry_timeout=10 -2 $SRM_ENDPOINT
        srmcp -retry_num=2 -retry_timeout=10 -2 file:///$FILE $SRM_ENDPOINT/$REMOTE_FILE
        srmls -retry_num=2 -retry_timeout=10 -2 $SRM_ENDPOINT | grep $REMOTE_FILE
        #srmcp -retry_num=2 -retry_timeout=10 -2 $SRM_ENDPOINT/$REMOTE_FILE file:///$FILE2
        #diff $FILE $FILE2
        srmrm -retry_num=2 -retry_timeout=10 -2 $SRM_ENDPOINT/$REMOTE_FILE
        ;;
    gfal2-util)
        gfal-ls $SRM_ENDPOINT
        gfal-copy file:$FILE $SRM_ENDPOINT/$REMOTE_FILE
        gfal-ls $SRM_ENDPOINT/$REMOTE_FILE
        gfal-cat $SRM_ENDPOINT/$REMOTE_FILE
        rm -f $FILE2
        gfal-copy $SRM_ENDPOINT/$REMOTE_FILE file:$FILE2
        diff $FILE $FILE2
        gfal-rm $SRM_ENDPOINT/$REMOTE_FILE
        ;;
    gfal2-python)
        python bin/srm/gfal2/gfal2_simple_listing.py $SRM_ENDPOINT
        python bin/srm/gfal2/gfal2_long_listing.py $SRM_ENDPOINT
        python bin/srm/gfal2/gfal2_copy.py file:$FILE $SRM_ENDPOINT/$REMOTE_FILE
        python bin/srm/gfal2/gfal2_bring_online.py $SRM_ENDPOINT/$REMOTE_FILE
        python bin/srm/gfal2/gfal2_get_turls.py $SRM_ENDPOINT/$REMOTE_FILE
        #python bin/srm/gfal2/gfal2_python_read.py $SRM_ENDPOINT
        ;;
    *)
        echo "Not a supported client: $2" && exit 1
esac

set +x
set +e 

echo "Tests succeded!"
rm -f $FILE
rm -f $FILE2

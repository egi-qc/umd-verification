#!/bin/bash

#
# tests for srm compliance using storm SRM client
#

HOST=`hostname -f`

STORM_FE=httpg://$HOST:8444
SRM_URI=srm://$HOST:8444

STDOUT=`mktemp`
DIR=`basename $STDOUT`

execute() {
        echo ">> Executing $*"
        "$@" 2>&1 > $STDOUT
        if [ $? -ne 0 ] ; then
                echo "[ERROR]"
                cat $STDOUT
                exit 1
        fi
        echo "[OK]"
}

executeSRM() {
    execute "$@"
    cat $STDOUT | grep "SRM_SUCCESS" > /dev/null
    if [ $? -ne 0 ] ; then
        echo "[ERROR]"
        cat $STDOUT
        exit 1
    fi
   echo "[OK]"
}

get_file() {
        # $1 -> protocol
        # $2 -> srm location
        # $3 -> file to compare with
        executeSRM clientSRM ptg -e $STORM_FE -s $2 -p -T -P $1
        REQUEST_TOKEN=`cat $STDOUT | grep requestToken | cut -f2 -d"=" | tr -d '"'`
        TURL=`cat $STDOUT | grep "transferURL=" | cut -f2 -d"=" | tr -d '"'`
        echo "Getting file from $TURL (token: $REQUEST_TOKEN)"
        executeSRM clientSRM statusptg -e $STORM_FE -t $REQUEST_TOKEN
        cat $STDOUT | grep "SRM_FILE_PINNED" > /dev/null
        if [ $? -ne 0 ] ; then
                echo "<< Unexpected srm status!?"
                echo "OUTPUT: "
                cat $STDOUT
                exit 1
        fi
        GET_TEST_FILE=`mktemp`
        if [ $1 = "gsiftp" ] ; then
                execute uberftp $TURL file://$GET_TEST_FILE
        elif [ $1 = "https" ] ; then
                # FIXME: this should be verify = True
                execute python2.6 -c "import requests; r = requests.get(\"$TURL\", cert=\"$X509_USER_PROXY\", verify=False); open(\"$GET_TEST_FILE\", 'w+').write(r.text)"
        fi
        if [ $? -ne 0 ] ; then
                echo "<< Unexpected copy status!?"
                exit 1
        fi
        diff -u $3 $GET_TEST_FILE
        if [ $? -ne 0 ] ; then
                echo "<< Files differ!?"
                exit 1
        fi
        executeSRM clientSRM rf -e $STORM_FE -s $2 -t $REQUEST_TOKEN
        executeSRM clientSRM statusptg -e $STORM_FE -t $REQUEST_TOKEN
        cat $STDOUT | grep "SRM_RELEASED" > /dev/null
        if [ $? -ne 0 ] ; then
                echo "<< Unexpected srm status!?"
                echo "OUTPUT: "
                cat $STDOUT
                exit 1
        fi
        rm $GET_TEST_FILE
}

put_file() {
        # $1 -> protocol
        # $2 -> srm location
        # $3 -> file to transfer
        executeSRM clientSRM ptp -e $STORM_FE -s $2,150000 -p -T -P $1
        REQUEST_TOKEN=`cat $STDOUT | grep requestToken | cut -f2 -d"=" | tr -d '"'`
        TURL=`cat $STDOUT | grep "TURL=" | cut -f2 -d"=" | tr -d '"'`

        executeSRM clientSRM statusptp -e $STORM_FE -t $REQUEST_TOKEN -vN

        if [ $1 = "gsiftp" ] ; then
                execute uberftp file://$3 $TURL
        elif [ $1 = "https" ] ; then
                execute python2.6 -c "import requests; r = requests.put(\"$TURL\", cert=\"$X509_USER_PROXY\", verify=False, data=open(\"$3\").read())"
        fi
        if [ $? -ne 0 ] ; then
                echo "<< Copy failed!"
                exit 1
        fi

        executeSRM clientSRM pd -e $STORM_FE -s $2 -t $REQUEST_TOKEN

        executeSRM clientSRM statusptp -e $STORM_FE -t $REQUEST_TOKEN -vN
}


echo ">> Proxy info:"
voms-proxy-info -all
echo ""


VO=`voms-proxy-info -vo`
X509_USER_PROXY=`voms-proxy-info -path`


HTTPS_SUPPORT=0
GSIFTP_SUPPORT=0
executeSRM clientSRM gtp -e $STORM_FE
cat $STDOUT | grep "transferProtocol.*https" > /dev/null && HTTPS_SUPPORT=1
cat $STDOUT | grep "transferProtocol.*gsiftp" > /dev/null && GSIFTP_SUPPORT=1

executeSRM clientSRM mkdir -e $STORM_FE -s $SRM_URI/$VO/$DIR/

executeSRM clientSRM ls -e $STORM_FE -s $SRM_URI/$VO/$DIR/  -l

TEST_FILE=`mktemp`
cat > $TEST_FILE << EOF
This is a simple test
$RANDOM
$RANDOM
$RANDOM
EOF

if [ $GSIFTP_SUPPORT -eq 1 ] ; then
        echo ""
        echo "** Testing gsiftp PUT support"
        put_file gsiftp $SRM_URI/$VO/$DIR/test_file00.txt $TEST_FILE
fi
if [ $HTTPS_SUPPORT -eq 1 ] ; then
        echo ""
        echo "** Testing https PUT support"
        put_file https $SRM_URI/$VO/$DIR/test_file02.txt $TEST_FILE
fi


executeSRM clientSRM mv -e $STORM_FE -s $SRM_URI/$VO/$DIR/test_file00.txt -t $SRM_URI/$VO/$DIR/test_file01.txt

if [ $GSIFTP_SUPPORT -eq 1 ] ; then
        echo ""
        echo "** Testing gsiftp GET support"
        get_file gsiftp $SRM_URI/$VO/$DIR/test_file01.txt $TEST_FILE
fi

if [ $HTTPS_SUPPORT -eq 1 ] ; then
        echo ""
        echo "** Testing https GET support"
        get_file https $SRM_URI/$VO/$DIR/test_file02.txt $TEST_FILE
        executeSRM clientSRM rm -e $STORM_FE -s $SRM_URI/$VO/$DIR/test_file02.txt
fi


executeSRM clientSRM rm -e $STORM_FE -s $SRM_URI/$VO/$DIR/test_file01.txt

executeSRM clientSRM Rmdir -e $STORM_FE -s $SRM_URI/$VO/$DIR/

echo ""
echo ""
echo "<< All tests succeded!"

rm $STDOUT

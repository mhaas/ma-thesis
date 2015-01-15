#!/bin/bash

source `dirname $0`/train_common.sh

echo "Args: $@"

function main() {
    clusters=$1
    splitsdir=$2
    i=$3
    mode=$4
    NUM_HID=$5
    BATCH_SIZE=$6
    export NUM_HID
    export BATCH_SIZE
    # make transform_ptb_with_cluster use the right input 
    SPLITS_DIR=$splitsdir
    export SPLITS_DIR
    base=`basename $clusters`
    # $directory holds the cluster source
    directory=`dirname $clusters`
    directory=`basename $directory`
    # go back up two directories 
    basedir=`dirname $splitsdir`
    basedir=`dirname $basedir`
    newsplitsdir=$basedir/thesis-UPTRAIN_GST_CLUSTER_885_DIV/$directory.$mode.$base
    if [[ -n $NUM_HID && -n $BATCH_SIZE ]]; then
        newsplitsdir=$newsplitsdir.numHid_${NUM_HID}_batchSize_${BATCH_SIZE}
    fi
    mkdir -p $newsplitsdir
    cp -r $splitsdir $newsplitsdir || exit 1
    outdir=$newsplitsdir.rntn
    mkdir -p $outdir
    echo "For splits $splitsdir, applying divided $clusters. Result in $newsplitsdir"
    divide_clusters $mode $clusters $splitsdir $i $newsplitsdir
    train $i $newsplitsdir $outdir #"devset" 
}


main $@ 

#!/bin/bash

# This script divides cluster in sub-clusters based on prior sentiment polarity,
# applies the sub-clusters to the GST data and trains the RNTN on it.

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
    base=`basename $clusters`
    directory=`dirname $clusters`
    directory=`basename $directory`
    newsplitsdir=`dirname $splitsdir`/thesis-DIV_OPT_C5000/$directory.$mode.$base
    if [[ -n $NUM_HID && -n $BATCH_SIZE ]]; then
        newsplitsdir=$newsplitsdir.numHid_${NUM_HID}_batchSize_${BATCH_SIZE}
    fi
    cp -r $splitsdir $newsplitsdir 
    #mkdir -p $newsplitsdir
    outdir=$newsplitsdir.rntn
    mkdir -p $outdir
    echo "For splits $splitsdir, applying divided $clusters. Result in $newsplitsdir"
    divide_clusters $mode $clusters $splitsdir $i $newsplitsdir
    train "$i" "$newsplitsdir" "$outdir" #"devset" 
}


main $@ 

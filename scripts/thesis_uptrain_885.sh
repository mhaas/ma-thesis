#!/bin/bash

# This script adds noisily labelled data to the GST and trains the RNTN on that


source `dirname $0`/train_common.sh

echo "Args: $@"

function main() {
    splitsdir=$1
    i=$2
    NUM_HID=$3
    BATCH_SIZE=$4
    GST_WEIGHT=$5
    export NUM_HID
    export BATCH_SIZE
    # four days should be enough
    MAX_TRAIN_TIME="345600"
    export MAX_TRAIN_TIME
    newsplitsdir=`dirname $splitsdir`/thesis-UPTRAIN_GST_885/vanilla_GST_WEIGHT_${GST_WEIGHT}
    if [[ -n $NUM_HID && -n $BATCH_SIZE ]]; then
        newsplitsdir=$newsplitsdir.numHid_${NUM_HID}_batchSize_${BATCH_SIZE}
    fi
    mkdir -p $newsplitsdir
    cp -r $splitsdir/fold_$i/ $newsplitsdir || exit 1
    projdir=$DATADIR/film-rezensionen.de/thesis-amazon_885_projection/fold_$i
    mkdir -p $projdir
    # empty the file
    > $newsplitsdir/fold_${i}/train
    # How many times do we add the GST to the training data?    
    for indexVariable in `seq 1 $GST_WEIGHT`; do
        cat $splitsdir/fold_${i}/train  >> $newsplitsdir/fold_${i}/train || exit 2
    done 
    cat $projdir/predicted >> $newsplitsdir/fold_${i}/train || exit 3 
    outdir=${newsplitsdir}.rntn
    mkdir -p $outdir
    echo "newsplitsdir: $newsplitsdir"
    train $i $newsplitsdir $outdir 
}

main $@ 

#!/bin/bash

source `dirname $0`/train_common.sh

function train_mzn_split() {
    splitsdir=$1
    i=$2
    NUM_HID=$3
    BATCH_SIZE=$4
    export NUM_HID
    export BATCH_SIZE
    base=`basename $splitsdir`
    out=~/ma/film-rezensionen.de/rntn_param_est
    mkdir -p $out
    outfile=numHid_${NUM_HID}_batchSize_${BATCH_SIZE}
    out=$out/$base.$outfile
    mkdir $out.rntn
    train $i $splitsdir $out.rntn devset 
}

echo "Args: $@"

train_mzn_split $1 $2 $3 $4

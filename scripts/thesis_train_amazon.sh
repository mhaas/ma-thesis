#!/bin/bash

source `dirname $0`/train_common.sh

function train_mzn_split() {
    NUM_HID="25"
    BATCH_SIZE="22"
    export NUM_HID
    export BATCH_SIZE
    fold=$1
    sb=$2
    cutoff=$3
    input=$DATADIR/brown-cluster/affordable_useful_35182.txt-c1000-p1.out
    base=`basename $input`
    infile=clusters_over_${cutoff}_${sb}sb
    out=$DATADIR/film-rezensionen.de/thesis-MZN-CLUSTER-C1000-OPT/german_sentiment_treebank_592_beta_splits.$base.$infile
    mkdir -p $out
    transform_ptb_with_cluster $fold $input/$infile $out
    mkdir -p $out.rntn
    train $fold $out $out.rntn
}

train_mzn_split $@

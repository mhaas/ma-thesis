#!/bin/bash

source `dirname $0`/train_common.sh

function train_tueba_split() {
    NUM_HID="25"
    BATCH_SIZE="22"
    export NUM_HID
    export BATCH_SIZE
    fold=$1
    sb=$2
    cutoff=$3
    base=tueba_med20_paths
    infile=clusters_over_${cutoff}_${sb}sb
    out=$DATADIR/film-rezensionen.de/thesis-TUEBA-CLUSTER-OPT/german_sentiment_treebank_592_beta_splits.$base.$infile
    mkdir -p $out
    transform_ptb_with_cluster $fold $DATADIR/tueba_cluster/$infile $out
    mkdir -p $out.rntn
    train $fold $out $out.rntn
}
hostname
train_tueba_split $@

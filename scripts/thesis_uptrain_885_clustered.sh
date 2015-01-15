#!/bin/bash

source `dirname $0`/train_common.sh

function train_mzn_split() {
    fold=$1
    clusterfile=$2
    SPLITS_DIR=$3
    export SPLITS_DIR
    NUM_HID="25"
    BATCH_SIZE="22"
    export NUM_HID
    export BATCH_SIZE
    # four days should be enough
    MAX_TRAIN_TIME="345600"
    export MAX_TRAIN_TIME
    # used by transform_ptb_with_cluster
    base=`dirname $clusterfile`
    base=`basename $base`
    infile=`basename $clusterfile`
    splitsbase=`basename $SPLITS_DIR`
    out=$DATADIR/film-rezensionen.de/thesis-UPTRAIN_GST_CLUSTER_885/german_sentiment_treebank_592_beta_splits.$base.$splitsbase.$infile
    mkdir -p $out
    transform_ptb_with_cluster $fold $clusterfile $out
    mkdir -p $out.rntn
    train $fold $out $out.rntn
}

train_mzn_split $@

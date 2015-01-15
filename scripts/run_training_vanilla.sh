#!/bin/bash

source `dirname $0`/run_train_common.sh
base=~/ma/film-rezensionen.de/ 
in=german_sentiment_treebank_592_beta_splits
out=german_sentiment_treebank_592_beta_splits.rntn
mkdir -p $base/$out
parallel $PARALLEL_OPTS --joblog ~/ma/rntn_proj.joblog --sshlogin $HOSTS train.sh {} $base/$in $base/$out ::: `seq 0 9`


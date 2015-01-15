#!/bin/bash

# Sets up sentiment sub-clusters and runs training

source `dirname $0`/run_train_common.sh


NUM_HID=25
BATCH_SIZE=22


parallel $PARALLEL_OPTS $@ --joblog $JOBLOGDIR/thesis-run-uptraining-885.joblog \
    --sshlogin $HOSTS $CODEDIR/scripts/thesis_uptrain_885.sh {1} {2} $NUM_HID $BATCH_SIZE {3} \
    ::: $DATADIR/film-rezensionen.de/german_sentiment_treebank_592_beta_splits/ \
    ::: `seq 0 9` \
    ::: 0 1 23

cd $DATADIR/film-rezensionen.de/thesis-UPTRAIN_GST_885/ 

for i in *rntn; do
    $CODEDIR/scripts/thesis_merge_csv_average_testset.py $i
    $CODEDIR/scripts/naacl_eval_productions.sh $SPLITS $i
    $CODEDIR/scripts/naacl_contrastive_conjunctions.sh $SPLITS $i $PARSES
done
$CODEDIR/scripts/thesis_combine_uptrain.py  .


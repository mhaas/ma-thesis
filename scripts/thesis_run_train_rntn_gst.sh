#!/bin/bash

# Train RNTN on GST

source `dirname $0`/run_train_common.sh

OUTDIR=$DATADIR/film-rezensionen.de/german_sentiment_treebank_592_beta_splits.rntn

parallel $PARALLEL_OPTS $@ \
    --joblog $JOBLOGDIR/thesis_run_train_rntn_gst.log \
    --sshlogin $HOSTS \
    $CODEDIR/scripts/thesis_train_rntn_gst.sh {1} $SPLITS $OUTDIR ::: `seq 0 9`

python $CODEDIR/scripts/thesis_merge_csv_average_testset.py $OUTDIR


$CODEDIR/scripts/naacl_eval_productions.sh $SPLITS $OUTDIR
$CODEDIR/scripts/naacl_contrastive_conjunctions.sh $SPLITS $OUTDIR $PARSES

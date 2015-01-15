#!/bin/bash

BASE="$DATADIR/film-rezensionen.de/thesis-final-ensemble-gst"

source $CODEDIR/scripts/run_train_common.sh

FEATURES="--feature sentiws --feature regressionscore --feature projection --feature postags --feature count"
OUTDIR=$BASE/"thesis-final-ensemble-gst-top1"
parallel $PARALLEL_OPTS --sshlogin $POOL_HOSTS $CODEDIR/scripts/thesis_ensemble.sh {} "$OUTDIR" "$FEATURES" ::: `seq 0 9`
$CODEDIR/scripts/thesis_merge_csv_average_testset.py $OUTDIR
$CODEDIR/scripts/merge_csv_average_feature_importances.py $OUTDIR
$CODEDIR/scripts/naacl_eval_productions.sh $SPLITS $OUTDIR
$CODEDIR/scripts/naacl_contrastive_conjunctions.sh $SPLITS $OUTDIR $PARSES


FEATURES="--feature sentiws --feature regressionscore --feature projection --feature postags"
OUTDIR="$BASE/thesis-final-ensemble-gst-top2"
parallel $PARALLEL_OPTS --sshlogin $POOL_HOSTS $CODEDIR/scripts/thesis_ensemble.sh {} "$OUTDIR" "$FEATURES" ::: `seq 0 9`
$CODEDIR/scripts/thesis_merge_csv_average_testset.py $OUTDIR
$CODEDIR/scripts/merge_csv_average_feature_importances.py $OUTDIR
$CODEDIR/scripts/naacl_eval_productions.sh $SPLITS $OUTDIR
$CODEDIR/scripts/naacl_contrastive_conjunctions.sh $SPLITS $OUTDIR $PARSES


FEATURES="--feature sentiws --feature phrasesentiment --feature projection --feature postags"
OUTDIR="$BASE/thesis-final-ensemble-gst-top3"
parallel $PARALLEL_OPTS --sshlogin $POOL_HOSTS $CODEDIR/scripts/thesis_ensemble.sh {} "$OUTDIR" "$FEATURES" ::: `seq 0 9`
$CODEDIR/scripts/thesis_merge_csv_average_testset.py $OUTDIR
$CODEDIR/scripts/merge_csv_average_feature_importances.py $OUTDIR
$CODEDIR/scripts/naacl_eval_productions.sh $SPLITS $OUTDIR
$CODEDIR/scripts/naacl_contrastive_conjunctions.sh $SPLITS $OUTDIR $PARSES

FEATURES="--feature sentiws --feature phrasesentiment --feature projection --feature postags --feature count"
OUTDIR=$BASE/"thesis-final-ensemble-gst-top4"
parallel $PARALLEL_OPTS --sshlogin $POOL_HOSTS $CODEDIR/scripts/thesis_ensemble.sh {} "$OUTDIR" "$FEATURES" ::: `seq 0 9`
$CODEDIR/scripts/thesis_merge_csv_average_testset.py $OUTDIR
$CODEDIR/scripts/merge_csv_average_feature_importances.py $OUTDIR
$CODEDIR/scripts/naacl_eval_productions.sh $SPLITS $OUTDIR
$CODEDIR/scripts/naacl_contrastive_conjunctions.sh $SPLITS $OUTDIR $PARSES


FEATURES="--feature sentiws --feature phrasesentiment --feature regressionscore --feature projection --feature postags"
OUTDIR=$BASE/"thesis-final-ensemble-gst-top5"
parallel $PARALLEL_OPTS --sshlogin $POOL_HOSTS $CODEDIR/scripts/thesis_ensemble.sh {} "$OUTDIR" "$FEATURES" ::: `seq 0 9`
$CODEDIR/scripts/thesis_merge_csv_average_testset.py $OUTDIR
$CODEDIR/scripts/merge_csv_average_feature_importances.py $OUTDIR
$CODEDIR/scripts/naacl_eval_productions.sh $SPLITS $OUTDIR
$CODEDIR/scripts/naacl_contrastive_conjunctions.sh $SPLITS $OUTDIR $PARSES

FEATURES="--feature sentiws --feature phrasesentiment --feature regressionscore --feature projection --feature postags --feature count"
OUTDIR=$BASE/"thesis-final-ensemble-gst-top6"
parallel $PARALLEL_OPTS --sshlogin $POOL_HOSTS $CODEDIR/scripts/thesis_ensemble.sh {} "$OUTDIR" "$FEATURES" ::: `seq 0 9`
$CODEDIR/scripts/thesis_merge_csv_average_testset.py $OUTDIR
$CODEDIR/scripts/merge_csv_average_feature_importances.py $OUTDIR
$CODEDIR/scripts/naacl_eval_productions.sh $SPLITS $OUTDIR
$CODEDIR/scripts/naacl_contrastive_conjunctions.sh $SPLITS $OUTDIR $PARSES

combine_csv_ensemble.py $BASE

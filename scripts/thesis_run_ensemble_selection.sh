#!/bin/bash


source `dirname $0`/common.sh

FEATURES1='--feature sentiws'
FEATURES2='--feature sentiws --feature regressionscore'
FEATURES3='--feature sentiws --feature regressionscore --feature projection'
FEATURES4='--feature sentiws --feature regressionscore --feature projection --feature postags'
FEATURES5='--feature sentiws --feature regressionscore --feature projection --feature postags'
FEATURES6='--feature sentiws --feature phrasesentiment --feature projection --feature postags'
FEATURES7='--feature sentiws --feature regressionscore --feature projection --feature postags --feature count'


OUTDIR="$DATADIR/film-rezensionen.de/thesis-final-ensemble-20sentences/"
mkdir -p $OUTDIR
index=1
for feature in "$FEATURES1" "$FEATURES2" "$FEATURES3" "$FEATURES4" "$FEATURES5" "$FEATURES6" "$FEATURES7"; do 
    echo "$feature"
    mv  ${index}_ensemble.csv ${index}_ensemble.csv.back || true
    python $CODEDIR/ml/ensemble.py \
        --gold $DATADIR/film-rezensionen.de/second-sample/trees_gold \
        --projected $DATADIR/film-rezensionen.de/runs/twentyfirst_run/sample.xml \
        --mzn-reg-alphabet $DATADIR/mzn-reg-models-wo-singletons/alphabet_f56da36cf010264035535def0ca31b2c.pickle \
        --mzn-reg-model $DATADIR/mzn-reg-models-wo-singletons/lassocv_f56da36cf010264035535def0ca31b2c.pickle \
        --mzn-reg-args $DATADIR/ma/mzn-reg-models-wo-singletons/args_f56da36cf010264035535def0ca31b2c.pickle \
        --sentiws-pos  $DATADIR/sentiws/SentiWS_v1.8c_Positive.txt \
        --sentiws-neg $DATADIR/ma/sentiws/SentiWS_v1.8c_Negative.txt \
        --do-cv \
        --folds $DATADIR/second_sample_gold_folds.pickle \
        --learner SVC_linear \
        --learner RandomForest \
        --learner AdaBoost\
        --learner GradientBoosting \
        --learner ExtraTrees \
        $feature > $OUTDIR/${index}_ensemble.csv
    index=$(($index + 1))
done

for newIndex in `seq 1 $index`; do
    if [[ $newIndex -eq 1 ]]; then
        tailarg=0
    else
        tailarg=1
    fi
    tail -n $tailarg $OUTDIR/${newindex}_ensemble.csv > $OUTDIR/all_ensemble.csv
done
    

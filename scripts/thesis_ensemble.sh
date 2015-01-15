#!/bin/bash


# Run ensemble learner on GST data.

source `dirname $0`/train_common.sh

PATH="$PATH:$CODEDIR/ml/"
PATH="$PATH:$CODEDIR/scripts/"
export PATH
PYTHONPATH="$PYTHONPATH:$CODEDIR/shared/"
#PYTHONPATH="$PYTHONPATH:$CODEDIR"
export PYTHONPATH


function train_and_eval() {
    i=$1
    outdir=$2
    mkdir -p $outdir
    mkdir -p $outdir/fold_${i}
    shift 2
    features=$@
    echo "Features:"
    echo $features
    splitsdir=$SPLITS
    # $key is the identifier for the amazon regression run
    key="f56da36cf010264035535def0ca31b2c"
    evalTarget="test"
    if [[ -f $outdir/fold_${i}/${evalTarget}_predicted.ptb ]]; then
        echo "Output file exists, skipping training"
    else
        ensemble.py --gold $splitsdir/fold_$i/train \
            --projected $DATADIR/film-rezensionen.de/thesis-final-gst-proj-runs/projected-12/folds_xml/fold_$i/train \
            --mzn-reg-alphabet $DATADIR/mzn-reg-models-wo-singletons/alphabet_${key}.pickle \
            --mzn-reg-model $DATADIR/mzn-reg-models-wo-singletons/lassocv_${key}.pickle \
            --mzn-reg-args $DATADIR/mzn-reg-models-wo-singletons/args_${key}.pickle \
            --sentiws-pos $DATADIR/sentiws/SentiWS_v1.8c_Positive.txt \
            --sentiws-neg $DATADIR/sentiws/SentiWS_v1.8c_Negative.txt \
            --folds $splitsdir/fold_$i/train.sklearn_fold \
            $features\
            --classify-ptb-file $splitsdir/fold_$i/${evalTarget} --classify-as-test \
            --classify-projected $DATADIR/film-rezensionen.de/thesis-final-gst-proj-runs/projected-12/folds_xml/fold_$i/${evalTarget} \
            --classify-out $outdir/fold_${i}/${evalTarget}_predicted.ptb \
            --eval-csv /dev/null \
            --feature-weights-csv $outdir/feature_imp_$i.csv \
            --learner GradientBoosting
    fi
    thesis_eval $splitsdir/fold_$i/$evalTarget \
        $outdir/fold_${i}/${evalTarget}_predicted.ptb \
        $outdir/eval_${evalTarget}_split_${i}.csv
}
hostname
train_and_eval $@

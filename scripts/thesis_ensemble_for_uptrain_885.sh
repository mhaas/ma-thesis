#!/bin/bash

# Run ensemble learner on projected data.

source `dirname $0`/common.sh

PYTHONPATH="$PYTHONPATH:/$CODEDIR/shared/:$CODEDIR"


function train_and_predict() {
    i=$1
    splitsdir=$SPLITS
    outdir=$DATADIR/ma/film-rezensionen.de/thesis-amazon_885_projection/fold_$i
    mkdir -p $outdir
    ensemble.py --gold $splitsdir/fold_$i/train \
        --projected $DATADIR/film-rezensionen.de/thesis-final-gst-proj-runs/projected-12/folds/fold_$i/train \
        --mzn-reg-alphabet $DATADIR/mzn-reg-models-wo-singletons/alphabet_f56da36cf010264035535def0ca31b2c.pickle \
        --mzn-reg-model $DATADIR/mzn-reg-models-wo-singletons/lassocv_f56da36cf010264035535def0ca31b2c.pickle \
        --mzn-reg-args $DATADIR/mzn-reg-models-wo-singletons/args_f56da36cf010264035535def0ca31b2c.pickle \
        --sentiws-pos $DATADIR/3rdparty/sentiws/SentiWS_v1.8c_Positive.txt \
        --sentiws-neg $DATADIR/3rdparty/sentiws/SentiWS_v1.8c_Negative.txt \
        --feature regressionscore --feature sentiws \
        --feature postags --feature projection \
        --feature phrasesentiment --feature count \
        --classify-ptb-file $DATADIR/film-rezensionen.de/amazon_885_projection/885_de.latin-1.binarized.deepened.txt.out.140.stp \
        --classify-projected $DATADIR/film-rezensionen.de/885-proj-runs/2/mapped.xml \
        --classify-out $outdir/predicted \
        --learner GradientBoosting
}

echo $1
train_and_predict $1

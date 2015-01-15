#!/bin/bash

input="$DATADIR/amzn/newreleases_useful_best_1000.csv"
common="--input $input --skip-singletons --learner larscv --learner lassocv --learner lassolarscv"
common="$common --learner linsvr"
# will take ages otherwise :(
common="$common --alphabet-size 20000"
freq="--use-frequency"

echo "== Unigrams + FREQ =="
python $CODEDIR/ml/learn_mzn_review_score.py $common --use-unigrams $freq \
    > unigrams_freq.log &
echo "== Bigrams + FREQ =="
python $CODEDIR/ml/learn_mzn_review_score.py $common --use-bigrams $freq \
    > bigrams_freq.log &
echo "== Gappy Bigrams + FREQ =="
python $CODEDIR/ml/learn_mzn_review_score.py $common --use-gappy-bigrams $freq \
    > gappybigrams_freq.log &

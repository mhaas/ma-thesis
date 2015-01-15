#!/bin/bash

input="$DATADIR/amzn/newreleases_useful_best_1000.csv"
common="--input $input --skip-singletons --learner lassocv --learner linsvr"
# will take ages otherwise :(
common="$common --alphabet-size 80000"
out=${input}.shuffled


for n in 25 50 75 100; do
    python $CODEDIR/ml/learn_mzn_review_score.py $common --input $out/data_split_${n} --use-unigrams \
        > unigrams_data_${n}.log &
    python $CODEDIR/ml/learn_mzn_review_score.py $common --input $out/data_split_${n} --use-unigrams --use-bigrams \
        > unigrams_bigrams_data_${n}.log &
    python $CODEDIR/ml/learn_mzn_review_score.py $common --input $out/data_split_${n} --use-unigrams --use-bigrams --use-gappy-bigrams \
        > unigrams_bigrams_gappy_bigrams_data_${n}.log &
    python $CODEDIR/ml/learn_mzn_review_score.py $common --input $out/data_split_${n} --use-unigrams --use-gappy-bigrams \
        > unigrams_gappy_bigrams_data_${n}.log &
    python $CODEDIR/ml/learn_mzn_review_score.py $common --input $out/data_split_${n} --use-bigrams \
        > bigrams_data_${n}.log &
    python $CODEDIR/ml/learn_mzn_review_score.py $common --input $out/data_split_${n} --use-bigrams --use-gappy-bigrams \
        > bigrams_gappy_bigrams_data_${n}.log &
    python $CODEDIR/ml/learn_mzn_review_score.py $common --input $out/data_split_${n} --use-gappy-bigrams \
        > gappy_bigrams_data_${n}.log &
done

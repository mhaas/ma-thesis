#!/bin/bash

input="$DATADIR/amzn/newreleases_useful_best_1000.csv"
common="--input $input --skip-singletons --learner lassocv --learner linsvr"

for alpha in 20000 40000; do
    common="$common --alpha $alpha"
    python $CODEDIR/ml/learn_mzn_review_score.py $common --use-unigrams \
        > unigrams_alpha_${alpha}.log &
    python $CODEDIR/ml/learn_mzn_review_score.py $common --use-unigrams --use-bigrams \
        > unigrams_bigrams_alpha_${alpha}.log &
    python $CODEDIR/ml/learn_mzn_review_score.py $common  --use-unigrams --use-bigrams --use-gappy-bigrams \
        > unigrams_bigrams_gappy_bigrams_alpha_${alpha}.log &
    python $CODEDIR/ml/learn_mzn_review_score.py $common --use-unigrams --use-gappy-bigrams \
        > unigrams_gappy_bigrams_alpha_${alpha}.log &
    python $CODEDIR/ml/learn_mzn_review_score.py $common --use-bigrams \
        > bigrams_alpha_${alpha}.log &
    python $CODEDIR/ml/learn_mzn_review_score.py $common --use-bigrams --use-gappy-bigrams \
        > bigrams_gappy_bigrams_alpha_${alpha}.log &
    python $CODEDIR/ml/learn_mzn_review_score.py $common  --use-gappy-bigrams \
        > gappy_bigrams_alpha_${alpha}.log &
done

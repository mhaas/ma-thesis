#!/bin/bash

input="$DATADIR/amzn/newreleases_useful_best_1000.csv"
common="--input $input --skip-singletons --learner larscv --learner lassocv --learner lassolarscv"
common="$common --learner randomizedlasso --learner linsvr"
# will take ages otherwise :(
common="$common --alphabet-size 20000"

echo "== Unigrams =="
python $CODEDIR/ml/learn_mzn_review_score.py $common --use-unigrams \
    > unigrams.log &
echo "== Unigrams + TF-IDF =="
python $CODEDIR/ml/learn_mzn_review_score.py $common --use-unigrams --use-tf-idf \
    > unigrams_tfidf.log &
echo "== Bigrams =="
python $CODEDIR/ml/learn_mzn_review_score.py $common --use-bigrams \
    > bigrams.log &
echo "== Bigrams + TF-IDF =="
python $CODEDIR/ml/learn_mzn_review_score.py $common --use-bigrams --use-tf-idf \
    > bigrams_tfidf.log &
echo "== Unigrams + Bigrams =="
python $CODEDIR/ml/learn_mzn_review_score.py $common --use-unigrams --use-bigrams \
    > unigrams_bigrams.log &
echo "== Unigrams + Bigrams + TF-IDF=="
python $CODEDIR/ml/learn_mzn_review_score.py $common --use-unigrams --use-bigrams --use-tf-idf \
    > unigrams_bigrams_tfidf.log &
echo "== Unigrams + Gappy Bigrams=="
python $CODEDIR/ml/learn_mzn_review_score.py $common --use-unigrams --use-gappy-bigrams \
    > unigrams_gappybigrams.log &
echo "== Unigrams + Bigrams + Gappy Bigrams=="
python $CODEDIR/ml/learn_mzn_review_score.py $common --use-unigrams --use-bigrams --use-gappy-bigrams \
    > unigrams_bigrams_gappybigrams.log &
echo "==Gappy Bigrams=="
python $CODEDIR/ml/learn_mzn_review_score.py $common --use-gappy-bigrams \
    > gappy_bigrams.log &

python $CODEDIR/ml/learn_mzn_review_score.py $common --use-bigrams --use-gappy-bigrams --use-tf-idf \
    > gappybigrams_tfidf.log &

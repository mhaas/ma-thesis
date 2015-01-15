#!/bin/bash

source `dirname $0`/run_train_common.sh
source `dirname $0`/train_common.sh

function do_the_deed() {
    splitsdir=$1
    shift
    golddir=$1
    shift
    targetdir=$1
    shift
    mkdir -p $targetdir
    for i in `seq 0 9`; do
        mkdir $targetdir/fold_${i}/
        python $CODEDIR/sentiws/naive_prediction.py \
            --parse $splitsdir/fold_$i/test \
            --predicted-trees-file $targetdir/fold_${i}/test_predicted.ptb \
           "$@" 
        thesis_eval $golddir/fold_$i/test \
            $targetdir/fold_${i}/test_predicted.ptb \
            $targetdir/eval_test_split_${i}.csv
    done
    thesis_merge_csv_average_testset.py $targetdir

    $CODEDIR/scripts/naacl_eval_productions.sh $golddir $targetdir
    $CODEDIR/scripts/naacl_contrastive_conjunctions.sh $golddir $targetdir $splitsdir

}


# we work on the parses for --pos-mode

function evaluate_all() {
    # $1 is trees to be processed, e.g. parses
    # $2 is gold trees
    # $3 is run name
    do_the_deed $1 $2 $DATADIR/$3/sentiws_noshift/ \
        --lexicon SentiWS

    do_the_deed $1 $2 $DATADIR/$3/sentiws_noshift_POS/ \
        --lexicon SentiWS \
        --pos-mode

    do_the_deed $1 $2 $DATADIR/$3/sentiws_polartshift/ \
        --lexicon SentiWS \
        --shift-finder PolArt

    do_the_deed $1 $2 $DATADIR/$3/sentiws_polartshift_POS/ \
        --lexicon SentiWS \
        --shift-finder PolArt \
        --pos-mode

    #do_the_deed $1 $2 $DATADIR/$3/polart_polartshift_POS/ \
    #    --lexicon PolArt \
    #    --shift-finder PolArt \
    #    --pos-mode

    #do_the_deed $1 $2 $DATADIR/$3/sentimergesilly_noshift/ \
    #    --lexicon SentiMergeSilly

    #do_the_deed $1 $2 $DATADIR/$3/sentimergesilly_noshift_POS/ \
    #    --lexicon SentiMergeSilly \
    #    --pos-mode

    #do_the_deed $1 $2 $DATADIR/$3/sentimergesilly_polartshift/ \
    #    --lexicon SentiMergeSilly \
    #    --shift-finder PolArt
    
    #do_the_deed $1 $2 $DATADIR/$3/sentimergesilly_polartshift_POS/ \
    #    --lexicon SentiMergeSilly \
    #    --shift-finder PolArt \
    #    --pos-mode
    
    #do_the_deed $1 $2 $DATADIR/$3/sentimergeprecision_noshift/ \
    #    --lexicon SentiMergePrecision

    #do_the_deed $1 $2 $DATADIR/$3/sentimergeprecision_noshift_POS/ \
    #    --lexicon SentiMergePrecision \
    #    --pos-mode

    #do_the_deed $1 $2 $DATADIR/$3/sentimergeprecision_polartshift/ \
    #    --lexicon SentiMergePrecision \
    #    --shift-finder PolArt
    
    #do_the_deed $1 $2 $DATADIR/$3/sentimergeprecision_polartshift_POS/ \
    #    --lexicon SentiMergePrecision \
    #    --shift-finder PolArt \
    #    --pos-mode

    #do_the_deed $1 $2 $DATADIR/$3/sentimergerecall_noshift/ \
    #    --lexicon SentiMergeRecall

    #do_the_deed $1 $2 $DATADIR/$3/sentimergerecall_noshift_POS/ \
    #    --lexicon SentiMergeRecall \
    #    --pos-mode

    #do_the_deed $1 $2 $DATADIR/$3/sentimergerecall_polartshift/ \
    #    --lexicon SentiMergeRecall \
    #    --shift-finder PolArt
    
    #do_the_deed $1 $2 $DATADIR/$3/sentimergerecall_polartshift_POS/ \
    #    --lexicon SentiMergeRecall \
    #    --shift-finder PolArt \
    #    --pos-mode


    #do_the_deed $1 $2 $DATADIR/$3/polclue_noshift/ \
    #    --lexicon GermanPolarityClues

    #do_the_deed $1 $2 $DATADIR/$3/polclue_noshift_POS/ \
    #    --lexicon GermanPolarityClues \
    #    --pos-mode
 
    #do_the_deed $1 $2 $DATADIR/$3/polclue_polartshift/ \
    #    --lexicon GermanPolarityClues \
    #    --shift-finder PolArt

    #do_the_deed $1 $2 $DATADIR/$3/polclue_polartshift/ \
    #    --lexicon GermanPolarityClues \
    #    --shift-finder PolArt \
    #    --pos-mode

    do_the_deed $1 $2 $DATADIR/$3/mznlasso_noshift/ \
        --lexicon MznLasso

    do_the_deed $1 $2 $DATADIR/$3/mznlasso_polartshift/ \
        --lexicon MznLasso \
        --shift-finder PolArt

    do_the_deed $1 $2 $DATADIR/$3/mznsvr_noshift/ \
        --lexicon MznSVR

    do_the_deed $1 $2 $DATADIR/$3/mznsvr_polartshift/ \
        --lexicon MznSVR \
        --shift-finder PolArt

    python $CODEDIR/scripts/thesis_combine.py $DATADIR/$3/
}



evaluate_all $PARSES $SPLITS "lexicon_based"

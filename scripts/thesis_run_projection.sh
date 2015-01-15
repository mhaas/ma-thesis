#!/bin/bash

source `dirname $0`/common.sh
source `dirname $0`/train_common.sh

DATA="$DATADIR/film-rezensionen.de/gst_projection_eval/"

DEXML=$DATA/gst_orig_sentences.cleaned.latin-1.binarized.deepened.txt.out.140.stp.xml 
ENXML=$DATA/gst_translated_sentences.cleaned.binarized.txt.stp.xml
ANNOTATIONS=$DATA/gst_translated_sentences.cleaned.binarized.txt.stp.sentiment_annotated_rntn.onlyparses



function do_eval() {
    echo "In do_eval:"
    echo "do_eval $@"
    # where gold data is stored
    GOLD_FOLDS=$1
    # where predicted data is stored
    OUT_FOLDS=$2
    # where CSV is to be stored
    OUT_EVAL=$3
    PARSE_FOLDS=$4
    ALIGNMENT_FILE=$5
    PROJ_MODE=$6
    ALIGNMENT_TYPE=$7
    for i in `seq 0 9`; do
    # just move for consistency
        mv $OUT_FOLDS/fold_$i/test $OUT_FOLDS/fold_$i/test_predicted.ptb
        thesis_eval $GOLD_FOLDS/fold_$i/test \
            $OUT_FOLDS/fold_$i/test_predicted.ptb \
            $OUT_EVAL/eval_test_split_${i}.csv
    done
    $CODEDIR/scripts/naacl_eval_productions.sh \
        $GOLD_FOLDS \
        $OUT_FOLDS
    mv $OUT_FOLDS/evaluate_productions.txt $OUT_EVAL/
    $CODEDIR/scripts/naacl_contrastive_conjunctions.sh \
        $GOLD_FOLDS \
        $OUT_FOLDS \
        $PARSE_FOLDS
    mv $OUT_FOLDS/contrastive_conjunctions.csv $OUT_EVAL/
    echo "ALIGNMENT_FILE: $ALIGNMENT_FILE" >> $OUT_EVAL/task_description.txt
    echo "PROJ_MODE: $PROJ_MODE" >> $OUT_EVAL/task_description.txt
    echo "ALIGNMENT_TYPE: $ALIGNMENT_TYPE" >> $OUT_EVAL/task_description.txt
}

# Alignment files produced by Lingua-Align


function project() {
    ALIGNMENT="$1"
    PROJ_MODE="$2"
    ALIGNMENT_TYPE="$3"
    # needs to be in inner loop
    OUT="$DATADIR/film-rezensionen.de/thesis-final-gst-proj-runs/"
    mkdir -p $OUT
    OUT_PROJ=$OUT/projected-$RUN/
    mkdir -p $OUT_PROJ
    # just cd so project.py internal log file ends up in right place
    cd $OUT_PROJ
    ALIGNMENT_FILE=$DATADIR/film-rezensionen.de/alignments/gst-predicted-alignments-${ALIGNMENT}-model.xml
    if [[ ! -f $OUT_PROJ/mapped.xml ]]; then
        echo $DEXML
        echo $ENXML
        echo $ALIGNMENT_TYPE
        python $CODEDIR/projection/project.py \
             --input $ENXML \
             --annotations $ANNOTATIONS \
            --target $DEXML \
            --alignment $ALIGNMENT_FILE \
            --output $OUT_PROJ/mapped.xml \
            $PROJ_MODE \
            $ALIGNMENT_TYPE \
            --strip-target-id-prefix > $OUT_PROJ/logfile.log
        if [[ $? != 0 ]]; then
            echo "Problem running project.py"
            exit 1
        fi
    else
        echo "Output file exists, skipping projection!"
    fi
    # TODO: how sane is the binargst_projection_eval
    if [[ ! -f $OUT_PROJ/mapped.ptb ]]; then
        $DATADIR/lingua-align/lingua-align/bin/tiger2penn $OUT_PROJ/mapped.xml > $OUT_PROJ/mapped.ptb
    fi
    OUT_FOLDS=$OUT_PROJ/folds/
    mkdir -p $OUT_FOLDS
    10foldcv.py --input $OUT_PROJ/mapped.ptb --output $OUT_FOLDS --thesis-mode
    if [[ $? != 0 ]]; then
        echo "Problem running 10foldcv.py"
        exit 1
    fi
    # required elsewhere.
    OUT_FOLDS_XML=$OUT_PROJ/folds_xml/
    mkdir -p $OUT_FOLDS_XML
    10foldcv.py --input $OUT_PROJ/mapped.xml --output $OUT_FOLDS_XML --thesis-mode
    if [[ $? != 0 ]]; then
        echo "Problem running 10foldcv.py"
        exit 1
    fi
    OUT_EVAL=$OUT/10fold_cv-$RUN/
    mkdir -p $OUT_EVAL
    do_eval $SPLITS $OUT_FOLDS $OUT_EVAL $PARSES "$ALIGNMENT_FILE" "$PROJ_MODE" "$ALIGNMENT_TYPE"
    if [[ $? != 0 ]]; then
        echo "Problem in do_eval"
        exit 1
    fi
    RUN=$(($RUN+1))
}



RUN=1

project "sophisticated" "--apply-parent-sentiment" "--alignment-types good --alignment-types fuzzy"
project "sophisticated" "--apply-parent-sentiment" "--alignment-types good"
project "sophisticated" "" "--alignment-types good" 
project "sophisticated" "" "--alignment-types good --alignment-types fuzzy"
project "sophisticated" "--map-root-sentiment" "--alignment-types good" 
project "sophisticated" "--map-root-sentiment" "--alignment-types good --alignment-types fuzzy"

project "simple" "--apply-parent-sentiment" "--alignment-types good --alignment-types fuzzy"
project "simple" "--apply-parent-sentiment" "--alignment-types good"
project "simple" "" "--alignment-types good" 
project "simple" "" "--alignment-types good --alignment-types fuzzy"
project "simple" "--map-root-sentiment" "--alignment-types good" 
project "simple" "--map-root-sentiment" "--alignment-types good --alignment-types fuzzy"



cd $OUT

for i in projected-*; do
    $CODEDIR/scripts/naacl_eval_productions.sh $SPLITS $i/folds/
    $CODEDIR/scripts/naacl_contrastive_conjunctions.sh $SPLITS $i/folds/ $PARSES
done

for i in 10fold_cv*; do
    $CODEDIR/scripts/thesis_merge_csv_average_testset.py $i
done

$CODEDIR/scripts/combine_csv_projection.py .

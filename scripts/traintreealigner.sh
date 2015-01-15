#!/bin/bash
# This script trains a model for lingua::align.
# Provide SIMPLE or COMPLEX as the first parameter to
# select a feature set.

PATH=$PATH:~/ma/lingua-align/lingua-align/bin/
INPUT="$DATADIR/3rdparty/smultron/smultron-3.0-complete/alignment.xml"
echo "Model will be trained from input file $INPUT"
mkdir -p model
MODEL="$DATADIR/film-rezensionen.de/alignments/model/"`basename $INPUT .xml`_`date +"%F_%R"`.model
echo "Model will be stored in ${MODEL}."

# word alignments -- correct path ??
# See ~/ma/lingua-align/lingua-align/examples/smultron for reference
ALIGN="$DATADIR/3rdparty/smultron/alignments-3.0/en-de/postcat_align/agreement/post-pts/"
ALIGN_VARIANT="inter" # inter, union, grow-diag, grow-diag-final
# Assuming DE is source and EN is target.
ALIGN_LANG="de-en"


# Test feature
#FEATURES="catpos:moses:parent_moses:children_moses"
FEATURES="treelevelsim:treespansim:catpos:parent_catpos:children_catpos"
MOSES_FEATURES="moses:parent_moses:children_moses"
FEATURES_SIMPLE=${FEATURES}:${MOSES_FEATURES}
# from europarl example Makefile
# nrleafsratio:parent_catpos:catpos.parent_catpos:treelevelsim:treespansim:treespansim*treelevelsim:giza:parent_giza:giza.catpos:moses:moses.catpos:sister_giza.catpos:sister_moses.catpos:moseslink:treespansim.catpos:treelevelsim.catpos:children_giza.catpos
# Most of the features from the example Makefile, minus giza features, plus some moses features
FEATURES_COMPLEX="nrleafsratio:parent_catpos:catpos.parent_catpos:treelevelsim:treespansim:treespansim*treelevelsim:moses:moses.catpos:sister_moses.catpos:moseslink:treespansim.catpos:treelevelsim.catpos:moses.parent_moses:children_moses"

if [[ x$1 == x"SIMPLE" ]]; then
    echo "Using SIMPLE feature set.";
    FEATURES=$FEATURES_SIMPLE;
elif [[ x$1 == x"COMPLEX" ]]; then
    echo "Using COMPLEX feature set.";
    FEATURES=$FEATURES_COMPLEX;
else
    echo "Unknown feature set requested. Exiting.";
    exit 1;
fi

    

echo "Using Features: $FEATURES"


CLASSIFIER="megam"

# triggers training mode, but not necessary since ${MODEL} does not exist
NR_TRAIN="3500"
#NR_DEV="10"
#NR_EVAL="10"

# what about number of dev set and test set using -V and -e?


# TODO: use -P, -C and -U for history-based features
CMD="treealign -v \
    -c ${CLASSIFIER} \
    -a ${INPUT} \
    -m ${MODEL} \
    -f ${FEATURES} \
    -n ${NR_TRAIN} \
    -y ${ALIGN}//${ALIGN_VARIANT}/europarl7/${ALIGN_LANG}/model/aligned.${ALIGN_VARIANT}"

echo "Running treealign: $CMD"
$CMD

    #-n ${NR_TRAIN} \
    #-e ${NR_DEV} \

#-y gives us access to moses* features
    #-I moses/model/aligned.ids \
    #-g moses/giza.src-trg/src-trg.A3.final.gz \
    #-G moses/giza.trg-src/trg-src.A3.final.gz \
    # ./agreement/post-pts/inter/europarl7/de-en/model/aligned.inter
    #-V ${NR_DEV} \
    #-e ${NR_TEST} \
    #-v \
    #-x ${ALIGNTHR} \
    #-l ${SEARCH} ${EXTRAOPT} \
    #> ${TRAINCORPUS}.${NR_TRAIN}.${NR_DEV}.align
#${BINDIR}/treealigneval ${TRAINCORPUS}.xml \
#    ${TRAINCORPUS}.${NR_TRAIN}.${NR_DEV}.align


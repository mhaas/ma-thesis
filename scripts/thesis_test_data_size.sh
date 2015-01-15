#!/bin/bash
# get CLASSPATH
source `dirname $0`/train_common.sh

if [[ x$1 == 'x' ]]; then
    echo "Please provide 'train' or 'test' argument"
    exit 5
fi

N=$2
INDIR=$3
OUTDIR=$4

echo $@

if [[ -z $N ]]; then
    echo "N is empty?!"
    exit 2
fi

mkdir -p $OUTDIR
cd $OUTDIR

if [[ $1 == "train" ]]; then
    target="train_${N}.txt"
    if [[ -f model_${N}.bin || -f model_${N}.bin.gz ]]; then
        echo "Model exists. Skipping training"
        exit 0
    fi
    head -n $N $INDIR/train.txt > $target;
    java -cp "$CLASSPATH" edu.stanford.nlp.sentiment.SentimentTraining \
        -train \
        -trainpath $target \
        -model model_${N}.bin 
elif [[ $1 == "test" ]]; then
    echo "Evaluating model for N=$N"
    target="train_${N}.txt"
    model="model_${N}.bin"
    echo `pwd`
    mv $model $model.gz
    java -cp "$CLASSPATH" edu.stanford.nlp.sentiment.SentimentPipeline \
        -input TREES -output PENNTREES \
        -sentimentModel `pwd`/$model.gz \
        -file $INDIR/test.txt \
        > test_${N}_predicted.ptb.withparses
    grep '^(' test_${N}_predicted.ptb.withparses \
        > test_${N}_predicted.ptb

    python $CODEDIR/shared/evaluate_system.py \
        --gold $INDIR/test.txt \
        --predicted test_${N}_predicted.ptb \
        --output-file all_${N}.csv
    if [[ $? != 0 ]]; then
        echo "Error running evaluate_system!"
        exit 10
    fi
    echo "Counting segments"
    count_segments.sh $target
    echo "Done for N=$N"
else
    echo "Unknown argument, must be 'train' or 'test'".
    exit -1
fi


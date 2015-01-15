
# This won't work for interactive shells
source `dirname $0`/common.sh
#source common.sh


# This script holds some common functions for training an RNTN model
unset CLASSPATH
CLASSPATH=$DATADIR/3rdparty/stanford-corenlp-full-2014-01-04/'*'
export CLASSPATH

PATH=$PATH:$CODEDIR/ml/
PATH=$PATH:$CODEDIR/scripts/
export PATH


PYTHONPATH="$PYTHONPATH:$CODEDIR/shared/"
PYTHONPATH="$PYTHONPATH:$CODEDIR"
export PYTHONPATH

# annotate clusters with sentiment label
# then apply annotated clusters to all PTB files for current fold
function divide_clusters() {
    mode=$1
    clusters=$2
    splitsdir=$3
    i=$4
    outdir=$5
    mkdir -p $outdir/fold_$i
    if [[ x$mode == x"sentiws" ]]; then
        script="apply_sentiws_to_clusters.py"
    elif [[ x$mode == x"ensemble" ]]; then
        # also need train file
        script="apply_mzn_sentiws_ensemble_to_clusters.py $splitsdir/fold_$i/train"
    elif [[ x$mode == x"mzn" ]]; then
        script="apply_mzn_dict_to_clusters.py"
    else
        print "Unknown mode $mode"
    fi
    if [[ ! -s $outdir/divided_clusters ]]; then 
        $script $clusters $outdir/divided_clusters 
    fi
    transform_ptb_with_cluster $i $outdir/divided_clusters $outdir 
}
function train() {
    randomSeed=250891
    i=$1
    splitsdir=$2
    outdir=$3
    if [[ x$4 == "x" ]]; then
        echo "Evaluating on test set!";
        evalTarget="test"
    elif [[ x$4 == "xdevset" ]]; then
        evalTarget="dev"
        echo "Evaluating on dev set!";
    else 
        echo "Unknown fourth parameter: must be empty or 'devset'."
        echo $@
        exit 1
    fi
    numHid=${NUM_HID:-25}
    batchSize=${BATCH_SIZE:-27}
    # default is one day
    trainTime=${MAX_TRAIN_TIME:-86400}
    echo "numHid set to $numHid"
    echo "batchSize set to $batchSize"
    echo "maxTrainTime set to $trainTime"
    echo "splitsdir: $splitsdir"
    echo "outdir: $outdir"
    mkdir -p $outdir/fold_${i}/
    modelFile=$outdir/fold_${i}.model
    if [[ -s $modelFile ]]; then
        echo "Model file $modelFile exists, skipping training";
    elif [[ -s $modelFile.gz ]]; then
        echo "Model file $modelFile.gz exists, Gunzipping and skipping training!";
        gunzip $outdir/fold_${i}.model.gz 

    else
        echo "Training on $splitsdir/fold_$i/train"
        java -cp "$CLASSPATH" edu.stanford.nlp.sentiment.SentimentTraining \
            -train -trainpath $splitsdir/fold_$i/train \
            -devpath $splitsdir/fold_$i/dev \
            -randomSeed $randomSeed \
            -numHid $numHid -batchSize $batchSize \
            -maxTrainTimeSeconds $trainTime \
            -model $outdir/fold_${i}.model.gz \
                2>&1 | tee $outdir/train_log_${i}.log 
        gunzip $outdir/fold_${i}.model.gz 
    fi
    echo "Training on $splitsdir/fold_$i/train finished."
    echo "Predicting $splitsdir/fold_$i/$evalTarget"
    java -cp "$CLASSPATH" edu.stanford.nlp.sentiment.SentimentPipeline \
        -input TREES -output PENNTREES \
        -sentimentModel $outdir/fold_${i}.model \
        -file $splitsdir/fold_$i/$evalTarget \
        > $outdir/fold_${i}/${evalTarget}_predicted.ptb \
        2> $outdir/predict_${evalTarget}_log_${i}.log
    if [[ $? != 0 ]]; then
        echo "Problem running SentimentPipeline."
        exit 4
    fi
    grep '^(' $outdir/fold_${i}/${evalTarget}_predicted.ptb \
        > $outdir/fold_${i}/${evalTarget}_predicted.ptb.new
    mv $outdir/fold_${i}/${evalTarget}_predicted.ptb.new \
        $outdir/fold_${i}/${evalTarget}_predicted.ptb
    echo "Finished predicting splitsdir/fold_$i/$evalTarget"
    echo "Evaluating -model $outdir/fold_${i}.model -treebank $splitsdir/fold_$i/$evalTarget"
    # thesis_eval also exists
    thesis_eval $splitsdir/fold_$i/$evalTarget \
        $outdir/fold_${i}/${evalTarget}_predicted.ptb \
        $outdir/eval_${evalTarget}_split_${i}.csv
    echo "Done evaluating"
}

function transform_ptb_with_cluster() {
    fold=$1
    clusters=$2
    outdir=$3
    if [[ -n $CLUSTER_LOWER ]]; then
        OPTS="--lower-case";
    fi
    if [[ -n $CLUSTER_STEM ]]; then
        OPTS="$OPTS --stem";
    fi
    if [[ -n "$CLUSTER_ONLY_POS_TAGS" ]]; then
        for posTag in $CLUSTER_ONLY_POS_TAGS; do
            OPTS="$OPTS --only-pos-tags $posTag"
        done
    fi
    if [[ -z $SPLITS_DIR ]]; then
        SPLITS_DIR="$DATADIR/film-rezensionen.de/german_sentiment_treebank_592_beta_splits/"
    fi
    echo "SPLITS_DIR is $SPLITS_DIR"
    echo "OPTS: $OPTS"
    mkdir -p $outdir/fold_${fold}
    for someSet in dev test train; do
        apply_cluster_to_ptb.py \
            --clusters $clusters \
            --ptb-input $SPLITS_DIR/fold_${fold}/${someSet} \
            --ptb-output $outdir/fold_${fold}/${someSet} $OPTS
            if [[ $? != 0 ]]; then
                hostname
                echo "Failure in apply_cluster_to_ptb: $@"
                exit 5
            fi
    done
}


function thesis_eval() {
    python $CODEDIR/shared/evaluate_system.py \
        --gold $1 \
        --predicted $2 \
        --output-file $3 
    if [[ $? != 0 ]]; then
        echo "Error running evaluate_system!"
        exit 10
    fi
}

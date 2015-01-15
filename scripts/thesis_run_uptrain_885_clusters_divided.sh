#!/bin/bash

# Sets up sentiment sub-clusters and runs training

source `dirname $0`/run_train_common.sh

NUM_HID=25
BATCH_SIZE=22

# This should be the best performing run
GST_WEIGHT=0
# This directory contains the uptraining data, e.g. the concatenation of GST
# and the noisily labelled data
FOLDS_DIR="$DATADIR/film-rezensionen.de/thesis-UPTRAIN_GST_885/vanilla_GST_WEIGHT_${GST_WEIGHT}.numHid_25_batchSize_22/"

parallel $PARALLEL_OPTS \
    --joblog $JOBLOGDIR/thesis_run_uptrain_885_clusters_divided.joblog \
    --sshlogin $HOSTS \
    $CODEDIR/scripts/thesis_uptrain_885_clusters_divided.sh {1} {2} {3} {4} ${NUM_HID} ${BATCH_SIZE} \
    ::: $DATADIR/brown-cluster/affordable_useful_35182.txt-c5000-p1.out/clusters_over_0_9sb \
        $DATADIR/brown-cluster/affordable_useful_35182.txt-c5000-p1.out/clusters_over_0_8sb \
        $DATADIR/brown-cluster/affordable_useful_35182.txt-c5000-p1.out/clusters_over_10_8sb \
    ::: $FOLDS_DIR \
    ::: `seq 0 9` \
    ::: sentiws ensemble

cd $DATADIR/film-rezensionen.de/thesis-UPTRAIN_GST_CLUSTER_885_DIV/
for i in *; do
    # bash specific
    if [[ $i = *.rntn ]]; then
        echo "Skipping $i";
        continue
    fi
    $CODEDIR/scripts/thesis_merge_csv_average_testset.py $i
    $CODEDIR/scripts/naacl_eval_productions.sh $SPLITS $i
    $CODEDIR/scripts/naacl_contrastive_conjunctions.sh $SPLITS $i $PARSES
done

$CODEDIR/scripts/thesis_combine_clusters_divided.py .


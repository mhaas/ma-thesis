#!/bin/bash

# Applies various MZN clusters to GST + PROJ and runs RNTN training


source `dirname $0`/run_train_common.sh
# This should be the best performing run
GST_WEIGHT=23

FOLDS_DIR="$DATADIR/film-rezensionen.de/thesis-UPTRAIN_GST_885/vanilla_GST_WEIGHT_${GST_WEIGHT}.numHid_25_batchSize_22/"

parallel $PARALLEL_OPTS \
    --joblog $JOBLOGDIR/thesis_run_uptrain_885_clustered.joblog \
    --sshlogin $HOSTS \
    $CODEDIR/scripts/thesis_uptrain_885_clustered.sh {1} {2} {3} \
    ::: `seq 0 9` \
    ::: $DATADIR/brown-cluster/affordable_useful_35182.txt-c5000-p1.out/clusters_over_0_15sb \
        $DATADIR/brown-cluster/affordable_useful_35182.txt-c5000-p1.out/clusters_over_10_16sb \
        $DATADIR/brown-cluster/affordable_useful_35182.txt-c5000-p1.out/clusters_over_30_19sb \
    ::: $FOLDS_DIR

cd $DATADIR/film-rezensionen.de/thesis-UPTRAIN_GST_CLUSTER_885/

for i in *rntn; do
    $CODEDIR/scripts/thesis_merge_csv_average_testset.py $i
    $CODEDIR/scripts/naacl_eval_productions.sh $SPLITS $i
    $CODEDIR/scripts/naacl_contrastive_conjunctions.sh $SPLITS $i $PARSES
done
$CODEDIR/scripts/thesis_combine_uptrain_clusters.py .

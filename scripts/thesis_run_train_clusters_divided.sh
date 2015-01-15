#!/bin/bash

# Sets up sentiment sub-clusters and runs training

source `dirname $0`/run_train_common.sh


NUM_HID=25
BATCH_SIZE=22

parallel $PARALLEL_OPTS $@ --joblog $JOBLOGDIR/thesis_run_train_clusters_divided.joblog \
    --sshlogin $HOSTS ~/kurse/Master-Arbeit/code/scripts/thesis_train_clusters_divided.sh \
    {1} {2} {3} {4} ${NUM_HID} ${BATCH_SIZE} \
    :::  \
        $DATADIR/brown-cluster/affordable_useful_35182.txt-c5000-p1.out/clusters_over_0_8sb \
        $DATADIR/brown-cluster/affordable_useful_35182.txt-c5000-p1.out/clusters_over_0_9sb \
        $DATADIR/brown-cluster/affordable_useful_35182.txt-c5000-p1.out/clusters_over_0_11sb \
        $DATADIR/brown-cluster/affordable_useful_35182.txt-c5000-p1.out/clusters_over_0_15sb \
        $DATADIR/brown-cluster/affordable_useful_35182.txt-c5000-p1.out/clusters_over_0_18sb \
        $DATADIR/brown-cluster/affordable_useful_35182.txt-c5000-p1.out/clusters_over_10_8sb \
        $DATADIR/brown-cluster/affordable_useful_35182.txt-c5000-p1.out/clusters_over_10_12sb \
        $DATADIR/brown-cluster/affordable_useful_35182.txt-c5000-p1.out/clusters_over_10_13sb \
        $DATADIR/brown-cluster/affordable_useful_35182.txt-c5000-p1.out/clusters_over_10_15sb \
        $DATADIR/brown-cluster/affordable_useful_35182.txt-c5000-p1.out/clusters_over_10_16sb \
        $DATADIR/brown-cluster/affordable_useful_35182.txt-c5000-p1.out/clusters_over_30_10sb \
        $DATADIR/brown-cluster/affordable_useful_35182.txt-c5000-p1.out/clusters_over_30_17sb \
        $DATADIR/brown-cluster/affordable_useful_35182.txt-c5000-p1.out/clusters_over_30_19sb \
    ::: $DATADIR/film-rezensionen.de/german_sentiment_treebank_592_beta_splits \
    ::: `seq 0 9` \
    ::: sentiws ensemble


exit_code=$?
if [[ $exit_code != 0 ]]; then
    echo "Problem running parallel: exit code $exit_code"
    exit 1
fi

for i in $DATADIR/film-rezensionen.de/thesis-DIV_OPT_C5000/*; do
    # bash specific
    # the predicted files are supposed to reside in *rntn, but the scripts
    # apparently don't want to do that.
    if [[ $i = *.rntn || $i = *.csv || $i = *.txt ]]; then
        echo "Skipping $i";
        continue
    fi
    $CODEDIR/scripts/thesis_merge_csv_average_testset.py $i
    $CODEDIR/scripts/naacl_eval_productions.sh $SPLITS $i
    $CODEDIR/scripts/naacl_contrastive_conjunctions.sh $SPLITS $i $PARSES
done


# TODO
python $CODEDIR/scripts/thesis_combine_clusters_divided.py  $DATADIR/film-rezensionen.de/thesis-DIV_OPT_C5000/

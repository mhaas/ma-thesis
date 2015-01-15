#!/bin/bash

# Applies various MZN clusters to GST and runs RNTN training

source `dirname $0`/run_train_common.sh
parallel $PARALLEL_OPTS \
    --joblog $JOBLOGDIR/thesis_run_training_mzn_c5000_clusters.joblog \
    --sshlogin $HOSTS \
    $CODEDIR/scripts/thesis_train_amazon_c5000.sh {1} {2} {3} ::: `seq 0 9` ::: `seq 8 20` ::: 0 10 30




exit_code=$?
if [[ $exit_code != 0 ]]; then
    echo "Problem running parallel: exit code $exit_code"
    exit 1
fi

for i in $DATADIR/film-rezensionen.de/thesis-MZN-CLUSTER-C5000-OPT/*.rntn; do
    $CODEDIR/scripts/thesis_merge_csv_average_testset.py $i
    $CODEDIR/scripts/naacl_eval_productions.sh $SPLITS $i
    $CODEDIR/scripts/naacl_contrastive_conjunctions.sh $SPLITS $i $PARSES
done

python $CODEDIR/scripts/combine_rntn_clusters.py  $DATADIR/film-rezensionen.de/thesis-MZN-CLUSTER-C5000-OPT/

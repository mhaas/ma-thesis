#!/bin/bash

# This script runs a gridsearch across numHid and batchSize hyperparameters
# on the dev set.

source `dirname $0`/run_train_common.sh

parallel $PARALLEL_OPTS \
    --joblog $JOBLOGDIR/thesis_run_gridsearch_hyper_params.joblog\
    --sshlogin $HOSTS \
    $CODEDIR/scripts/thesis_gridsearch_hyper_parameters.sh {1} {2} {3} {4} \
    ::: $SPLITS \
    ::: `seq 0 9` \
    ::: `seq 25 2 35` \
    ::: `seq 20 2 30`

for i in $DATADIR/film-rezensionen.de/rntn_param_est/*; do
    python $CODEDIR/scripts/thesis_merge_csv_average_devset.py $i;
done
python $CODEDIR/scripts/combine_rntn_param_est_csv.py \
    $DATADIR/film-rezensionen.de/rntn_param_est/

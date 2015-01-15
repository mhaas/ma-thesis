#!/bin/bash


source `dirname $0`/run_train_common.sh

parallel $PARALLEL_OPTS \
    --sshlogin $HOSTS \
    $CODEDIR/scripts/thesis_ensemble_for_uptrain_885.sh {} ::: `seq 0 9`

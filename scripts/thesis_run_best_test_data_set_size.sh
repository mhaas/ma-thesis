#!/bin/bash

if [[ x$1 == 'x' ]]; then
    echo "Please provide 'train' or 'test' argument"
    exit -1
fi
source `dirname $0`/run_train_common.sh


INDIR="$DATADIR/stanford_data/trees/"
OUTDIR="$DATADIR/thesis-rntn-stanforddata-size/"

parallel $PARALLEL_OPTS \
    --sshlogin $HOSTS \
    --joblog $JOBLOGDIR/rntn_size.joblog \
    --sshlogin $HOSTS $CODEDIR/scripts/thesis_test_data_size.sh $1 {} $INDIR $OUTDIR ::: `seq 0 500 8544`


if [[ $1 == 'test' ]]; then
        python $CODEDIR/scripts/combine_data_size_runs.py $OUTDIR
fi  


#!/bin/bash

if [[ x$1 == 'x' ]]; then
    echo "Please provide 'train' or 'test' argument"
    exit -1
fi
source `dirname $0`/run_train_common.sh

INDIR=$DATADIR/en_review_clusters/all_dvd_reviews.txt-c1000-p1.over_0_15sb.trees/
OUTDIR="$DATADIR/thesis-rntn-stanforddata-size.all_dvd_reviews.txt-c1000-p1.over_0_15sb/"

parallel $PARALLEL_OPTS \
    --sshlogin $HOSTS \
    --joblog $JOBLOGDIR/rntn_size_clusters.joblog \
    --sshlogin $HOSTS $CODEDIR/scripts/thesis_test_data_size.sh $1 {} $INDIR $OUTDIR ::: `seq 0 500 8544`

python $CODEDIR/scripts/combine_data_size_runs.py $OUTDIR

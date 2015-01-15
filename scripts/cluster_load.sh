#!/bin/bash

# Applies various MZN clusters to GST and runs RNTN training

# We used to do threshold = 30; but that's too much already.
# And training costs a lot of time!
# Maybe for TueBa again.

source `dirname $0`/run_train_common.sh
parallel -j0 -S $HOSTS --nonall --tag  $CODEDIR/scripts/cluster_load_single.sh

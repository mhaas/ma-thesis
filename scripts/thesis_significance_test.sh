#!/bin/bash

source `dirname $0`/common.sh

GOLDDIR=$1
SYSA=$2
SYSB=$3

goldfile=`mktemp`
sysafile=`mktemp`
sysbfile=`mktemp`

for i in `seq 0 9`; do
    cat $GOLDDIR/fold_$i/test >> $goldfile
    cat $SYSA/fold_$i/test_predicted.ptb >> $sysafile
    cat $SYSB/fold_$i/test_predicted.ptb >> $sysbfile
done

python $CODEDIR/shared/rand_approx_test.py \
    --gold $goldfile \
    --system-a $sysafile \
    --system-b $sysbfile \
    --p 0.05

rm $goldfile
rm $sysafile
rm $sysbfile

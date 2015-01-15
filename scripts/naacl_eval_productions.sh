#!/bin/bash

source `dirname $0`/common.sh

GOLDDIR=$1
EVALDIR=$2

goldfile=`mktemp`
predfile=`mktemp`

for i in `seq 0 9`; do
    cat $GOLDDIR/fold_$i/test >> $goldfile
    cat $EVALDIR/fold_$i/test_predicted.ptb >> $predfile
done

python $CODEDIR/shared/evaluate_productions.py \
    --gold $goldfile \
    --predicted $predfile \
    --granularity fine \
    --find-interesting \
    > $EVALDIR/evaluate_productions.txt

if [[ $? != 0 ]]; then
    echo "Problem running evaluate_productions.py!"
    exit 2
fi

# Does not really belong in here, but this gets called from everywhere
# So use it!

python $CODEDIR/shared/evaluate_at_length.py \
    --gold $goldfile \
    --predicted $predfile \
    --output-file $EVALDIR/accuracy_at_length.csv

if [[ $? != 0 ]]; then
    echo "Problem running evaluate_at_length.py!"
    exit 3
fi

rm $goldfile
rm $predfile

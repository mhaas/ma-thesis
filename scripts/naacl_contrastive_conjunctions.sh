#!/bin/bash

source `dirname $0`/common.sh

GOLDDIR=$1
EVALDIR=$2
PARSEDIR=$3

echo "GOLDDIR: $GOLDDIR"
echo "EVALDIR: $EVALDIR"
echo "PARSEDIR: $PARSEDIR"

# Although we have the full files for gold and parse,
# we need to re-assemble them in the correct order
# from the splits
goldfile=`mktemp`
predfile=`mktemp`
parsefile=`mktemp`
for i in `seq 0 9`; do
    cat $GOLDDIR/fold_$i/test >> $goldfile
    cat $EVALDIR/fold_$i/test_predicted.ptb >> $predfile
    cat $PARSEDIR/fold_$i/test >> $parsefile
done

# Get CLASSPATH with stanford jars
source `dirname $0`/train_common.sh
# And add my eval code to CLASSPATH
CLASSPATH="$CLASSPATH":$CODEDIR/MA/dist/MA.jar
export CLASSPATH


# Now perform the actual evaluation
java info.mhaas.ma.Evaluation.ContrastiveConjunctions \
        $parsefile \
        $goldfile \
        $predfile > $EVALDIR/contrastive_conjunctions.csv


rm $goldfile
rm $predfile
rm $parsefile 

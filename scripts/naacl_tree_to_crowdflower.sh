#!/bin/bash

source `dirname $0`/common.sh

# Everything is in UTF-8, although the file name suggests otherwise
# 1184 sentences
input=$DATADIR/film-rezensionen.de/fazits/txt-wo-quotes-fazits-clean-latin1.txt.out.100.stp
# deepen trees
wd=$NAACLDATADIR/crowdflower/
mkdir -p $wd
java -cp $CODEDIR/MA/dist/MA.jar info.mhaas.ma.PTBHandling.ConvertTrees \
    "$input" -deepen -binarize -collapseUnary -german -applyLabels \
    > $wd/txt-wo-quotes-fazits-clean-latin1.txt.out.100.stp.preproc 
echo "Preprocessed trees."
java -cp $CODEDIR/MA/dist/MA.jar info.mhaas.ma.PTBHandling.ExtractSegments \
    $wd/txt-wo-quotes-fazits-clean-latin1.txt.out.100.stp.preproc \
    | sort -u | shuf > $wd/txt-wo-quotes-fazits-clean-latin1.txt.out.100.stp.preproc.segments.uniq
echo "Extracted segments"
python $CODEDIR/cf/create_file.py \
    --segments $wd/txt-wo-quotes-fazits-clean-latin1.txt.out.100.stp.preproc.segments.uniq \
    --annotation $DATADIR/crowdflower/results_10_percent_half/a445105.csv \
    --annotation $DATADIR/crowdflower/results_20_percent_half/a445108.csv \
    --annotation $DATADIR/crowdflower/results_100_percent_half/a449779.csv \
    --annotation $DATADIR/crowdflower/results_100_percent_half_rest_comma/a451420.csv \
    --out $wd/unannotated_for_crowdflower.csv


 

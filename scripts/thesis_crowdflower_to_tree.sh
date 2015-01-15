#!/bin/bash


# Everything is in UTF-8, although the file name suggests otherwise
source `dirname $0`/common.sh

wd=$DATADIR/crowdflower/

# First, handle old annotations from the first 592 sentences.

# We had some duplicate annotations because the CSV in earlier annotation runs
# was broken.
# Let the majority vote decide for these.
# First, combine the _f_ull annotation data
outf=`mktemp`
cat $DATADIR/crowdflower/results_10_percent/f445105.csv \
        > $outf
tail -n +2 $DATADIR/crowdflower/results_20_percent/f445108.csv \
        >> $outf
tail -n +2 $DATADIR/crowdflower/results_100_percent/f449779.csv \
        >> $outf
tail -n +2 $DATADIR/crowdflower/results_100_percent_rest_comma/f451420.csv \
        >> $outf
# Second, combine the _a_ggregate annotation data
outa=`mktemp`
cat $DATADIR/crowdflower/results_10_percent/a445105.csv \
        > $outa
tail -n +2 $DATADIR/crowdflower/results_20_percent/a445108.csv \
        >> $outa
tail -n +2 $DATADIR/crowdflower/results_100_percent/a449779.csv \
        >> $outa
tail -n +2 $DATADIR/crowdflower/results_100_percent_rest_comma/a451420.csv \
        >> $outa
# Now, merge and deduplicate annotations
outtsv=$wd/annotations_445105_445108_449779_451420_deduplicated.tsv
python $CODEDIR/cf/merge_duplicate_crowdflower_annotations.py \
    $outf $outa $outtsv
rm $outa $outf

# Globally add removed punctuation back in
# The first run AFAIR did not have punctuation removed,
# but this is not a problem. Punctuation is only added back
# if there is no existing manual annotation
python $CODEDIR/scripts/back_to_punctuation.py \
    $DATADIR/film-rezensionen.de/fazits/fazits/txt-wo-quotes-fazits-clean-latin1.txt.out.100.stp.592.deepened-properly.binarized.segments \
    $outtsv \
    $wd/full_with_punctuation.tsv

# In the first two (or three?) annotation runs, the binarization code
# was iffy. Hence, some segments are annotated which do not actually exist
# in the parse trees anymore. These segments are deemed 'invalid'
# and removed
# Another source of superfluous segments is back_to_punctuation.py
# which can overgenerate.
python $CODEDIR/cf/retain_valid_segments.py \
    $wd/full_with_punctuation.tsv \
    $DATADIR/film-rezensionen.de/fazits/fazits/txt-wo-quotes-fazits-clean-latin1.txt.out.100.stp.592.deepened-properly.binarized \
    $DATADIR/film-rezensionen.de/fazits/fazits/txt-wo-quotes-fazits-clean-latin1.txt.out.100.stp.592.deepened-properly.binarized.segments \
    $wd/full.with_punctuation.valid_segments.tsv

mkdir -p $DATADIR/HeiST/
java -cp $CODEDIR/MA/dist/MA.jar info.mhaas.ma.Annotation.AnnotationToPTB \
    $wd/full.with_punctuation.valid_segments.tsv \
    $wd/txt-wo-quotes-fazits-clean-latin1.txt.out.100.stp.preproc \
    $DATADIR/HeiST/HeiST_592.ptb

echo "Done!"
echo "Results in $DATADIR/HeiST/HeiST_592.ptb"


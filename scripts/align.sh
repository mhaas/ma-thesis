#!/bin/bash
# This script producdes word alignments using PostCAT
# The files to be aligned must be in $DATA/en-de and named
# fm.lemma.de and fm.lemma.en

# Path to PostCAT
PC="/home/students/haas/ma/PostCAT/PostCAT-release-2/"
CLASSPATH="$CLASSPATH:${PC}/lib/postCAT-2.jar:${PC}/lib/trove-2.0.2.jar"
export CLASSPATH
# Path where the model resides
EP="/home/mitarb/versley/scratch/Europarlv7/"
# Language pair
F="en-de"
# Complete model path
BNAME="${EP}${F}/"
MODEL=${BNAME}postcat_model/
# Path to our data for which we create alignments

if [[ x$1 == x"SMULTRON" ]]; then
    echo "Using SMULTRON data.";
    DATA="$DATADIR/smultron/alignments-3.0/"
elif [[ x$1 == x"FILM" ]]; then
    echo "Using film-rezensionen.de data.";
    DATA="$DATADIR/film-rezensionen.de/word-alignments/"
elif [[ x$1 == x"GST" ]]; then
    echo "Using GST data.";
    DATA="$DATADIR/film-rezensionen.de/gst-word-alignments/"
elif [[ x$1 == x"592" ]]; then
    echo "Using 592 data.";
    DATA="$DATADIR/film-rezensionen.de/592-word-alignments/"
elif [[ x$1 == x"9682-mzn" ]]; then
    echo "Using 9682-mzn data.";
    DATA="$DATADIR/film-rezensionen.de/9682-mzn-word-alignments/"
else
    echo "Unknown data set requested. Exiting.";
    exit 1;
fi


# We will create the setup for postcat in this file
PARAMS="${DATA}/postcat.params"
# Where we store the alignments
ALIGNMENTS="${DATA}${F}/postcat_align/"
MODEL=${BNAME}postcat_model/
cat <<EOF > $PARAMS
name=europarl7
source_suffix=en
target_suffix=de
training_file=en-de/smultron.lemma
EOF

# Needs line number from trained model for some reason?
LINECOUNT=1959829
PC_METHOD=agreement
PC_MAXSIZE=40
PC_DECODE=post-pts
PC_THRESH=0.3
#corpusDescription = args[0];
#size = Integer.parseInt(args[1]);
#maxSentenceLen = Integer.parseInt(args[2]);
#modelDir = args[3];
#modelName = args[4];
#baseDir = args[5];
#decodingType = args[6];
#posterior = Float.parseFloat(args[7]);
cd $DATA
CMD="java -Xmx8G cat.programs.AlignmentsForMoses \
    $PARAMS $LINECOUNT \
    $PC_MAXSIZE $MODEL $PC_METHOD \
    $ALIGNMENTS $PC_DECODE $PC_THRESH"

echo "Running PostCAT command:"
echo $CMD
$CMD


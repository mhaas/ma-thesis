#!/bin/bash

if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Not running in virtualenv. This is probably bad."
fi


# You need to set these.
DATADIR="/mntpnts/theses_diddley/ss14/haas/ma/release/data/"
CODEDIR="/mntpnts/theses_diddley/ss14/haas/ma/release/code/"
if [[ -z "$DATADIR" || -z $CODEDIR ]]; then
    echo "Either DATADIR or CODEDIR variable is empty. Set both in common.sh."
    exit 1
fi


JOBLOGDIR="$DATADIR/parallel_logs/"
mkdir -p $JOBLOGDIR


PYTHONPATH=$CODEDIR:$PYTHONPATH
export PYTHONPATH


SPLITS=$DATADIR/film-rezensionen.de/german_sentiment_treebank_592_beta_splits
PARSES=$DATADIR/film-rezensionen.de/german_sentiment_treebank_592_beta_parses


export DATADIR
export CODEDIR
export SPLITS
export PARSES

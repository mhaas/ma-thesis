#!/usr/bin/env python

import sys
import combine_multiple_experiments
import re


def detailsExtractor(dirName):
    # german_sentiment_treebank_592_beta_splits.numHid_33_batchSize_20.rntn
    dirRegEx = re.compile(ur'(.*)\.numHid_(\d\d)_batchSize_(\d\d)\.rntn')
    match = dirRegEx.match(dirName)
    assert match
    source = match.group(1)
    numHid = match.group(2)
    batchSize = match.group(3)
    return [source, numHid, batchSize]


if __name__ == "__main__":
    header = ["source", "numHid", "batchSize"]
    combine_multiple_experiments.main(sys.argv[1], header, detailsExtractor)

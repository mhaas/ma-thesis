#!/usr/bin/env python

import sys
import combine_multiple_experiments
import re


def detailsExtractor(dirName):
    # german_sentiment_treebank_592_beta_splits.affordable_useful_35182.txt-c5000-p1.out.clusters_over_10_17sb
    dirRegEx = re.compile(ur'(.*)\.clusters_over_(\d{1,2})_(\d{1,2})sb\.rntn')
    match = dirRegEx.match(dirName)
    print dirName
    assert match
    source = match.group(1)
    threshold = match.group(2)
    sb = match.group(3)
    return [source, threshold, sb]


if __name__ == "__main__":
    header = ["source", "threshold", "sb"]
    combine_multiple_experiments.main(sys.argv[1], header, detailsExtractor,
                                      dirPattern='*.rntn')

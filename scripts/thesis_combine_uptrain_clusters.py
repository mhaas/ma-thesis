#!/usr/bin/env python

import sys
import re
import combine_multiple_experiments


def detailsExtractor(dirName):
    # german_sentiment_treebank_592_beta_splits.
    # [..] affordable_useful_35182.txt-c5000-p1.
    # [..] out.vanilla_GST_WEIGHT_23.
    # [..] numHid_25_batchSize_22.clusters_over_0_15sb
    regexS = ur'german_sentiment_treebank_592_beta_splits\.'
    regexS += ur'(.*)\.'
    regexS += ur'out\.vanilla_GST_WEIGHT_(\d{1,2})\.'
    regexS += ur'numHid_25_batchSize_22\.clusters_over_(\d{1,2})_(\d{1,2})sb'
    regex = re.compile(regexS)
    match = regex.match(dirName)
    assert match
    clusterSource = match.group(1)
    weight = match.group(2)
    threshold = match.group(3)
    bits = match.group(4)
    return [clusterSource, threshold, bits, weight]


if __name__ == '__main__':
    headers = ['Cluster Source', 'Freq Threshold',
               'Significant Bits', 'GST Weight']
    combine_multiple_experiments.main(sys.argv[1], headers,
                                      detailsExtractor,
                                      dirPattern='*rntn')

#!/usr/bin/env python

import sys
import re
import combine_multiple_experiments


def detailsExtractor(dirName):
    # affordable_useful_35182.txt-c5000-p1.
    # out.sentiws.clusters_over_10_8sb.
    # numHid_25_batchSize_22/
    regexS = ur'(.*)\.out\.'
    regexS += ur'(.*)\.clusters_over_(\d{1,2})_(\d{1,2})sb\.'
    regexS += ur'numHid_25_batchSize_22'
    regex = re.compile(regexS)
    match = regex.match(dirName)
    assert match
    clusterSource = match.group(1)
    div = match.group(2)
    threshold = match.group(3)
    bits = match.group(4)
    return [clusterSource, threshold, bits, div]


if __name__ == '__main__':
    headers = ['Cluster Source', 'Freq Threshold',
               'Significant Bits', 'Div Source']
    combine_multiple_experiments.main(sys.argv[1], headers,
                                      detailsExtractor,
                                      rejectPattern=re.compile(ur'.*\.rntn'))

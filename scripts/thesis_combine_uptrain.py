#!/usr/bin/env python

import sys
import re
import combine_multiple_experiments


def detailsExtractor(dirName):
    # vanilla_GST_WEIGHT_1.numHid_25_batchSize_22
    regexS = ur'vanilla_GST_WEIGHT_(\d{1,2})\.numHid_25_batchSize_22\.rntn'
    regex = re.compile(regexS)
    match = regex.match(dirName)
    assert match
    return [match.group(1)]

if __name__ == '__main__':
    combine_multiple_experiments.main(sys.argv[1], ['weight'],
                                      detailsExtractor,
                                      dirPattern='*rntn')

#!/usr/bin/env python

import sys
import combine_multiple_experiments


def detailsExtractor(dirName):
    return dirName

if __name__ == '__main__':
    combine_multiple_experiments.main(sys.argv[1], ['source'],
                                      detailsExtractor,
                                      dirPattern='folds*')

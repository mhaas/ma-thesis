#!/usr/bin/env python

import sys
import re

import combine_multiple_experiments


def detailsExtractor(dirName):
    regex = re.compile(ur'10fold_cv-(\d{1,2})')
    match = regex.match(dirName)
    assert match
    run = match.group(1)
    return [run]

if __name__ == '__main__':
    combine_multiple_experiments.main(sys.argv[1], ["run"],
                                      detailsExtractor,
                                      dirPattern='10fold_cv-*')

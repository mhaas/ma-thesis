#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import sys
import combine_multiple_experiments


def detailsExtractor(dirName):
    regex = re.compile(ur'thesis-final-ensemble-gst-top(\d{1})')
    match = regex.match(dirName)
    assert match
    run = match.group(1)
    return [run]

if __name__ == '__main__':
    runRE = re.compile(ur'thesis-final-ensemble-gst-top(\d{1})')
    globPattern = 'thesis-final-ensemble-gst-top?'
    combine_multiple_experiments.main(sys.argv[1], ['run'], detailsExtractor,
                                      dirPattern=globPattern)

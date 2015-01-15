#!/usr/bin/python
# -*- coding: utf-8 -*-

import sample
import sys

if __name__ == "__main__":
    sentences = sample.get_summaries(sys.argv[1])
    outFH = open(sys.argv[2], "w")
    for sentence in sentences:
        outFH.write(sentence[2])
    outFH.close()

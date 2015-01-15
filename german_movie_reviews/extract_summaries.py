#!/usr/bin/python
# -*- coding: utf-8 -*-

import sample
import sys
from collections import OrderedDict

if __name__ == "__main__":
    sentences = sample.get_summaries(sys.argv[1])
    outFH = open(sys.argv[2], "w")
    outFH2 = open(sys.argv[3], "w")
    tmp = OrderedDict()
    for s in sentences:
        curFile = s[0]
        if not curFile in tmp:
            tmp[curFile] = []
        tmp[curFile].append(s[2].replace("\n", " "))
    for (fileName, summaryFragments) in tmp.iteritems():
        outFH2.write(fileName)
        outFH2.write(" ")
        outFH2.write("N/A")
        outFH2.write(" ")
        outFH2.write(" ".join(summaryFragments))
        outFH2.write("\n")
    outFH2.close()
    for s in sentences:
        outFH.write(str(s[0]))
        outFH.write(" ")
        outFH.write(str(s[1]))
        outFH.write(" ")
        outFH.write(s[2].replace("\n", " "))
        outFH.write("\n")
    outFH.close()

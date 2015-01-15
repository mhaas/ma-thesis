#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import os


def main(inFile, outFile):
    fh = open(inFile)
    outFH = open(outFile, "w")
    writer = csv.writer(outFH)
    for line in fh.readlines():
        if line.strip() == "":
            continue
        res = {}
        row = []
        delim = " "
        if os.environ.get("DOTAB"):
            delim = "\t"
        tokens = line.strip().split(delim)
        doc = tokens[0]
        row.append(doc)
        source = tokens[1]
        row.append(source)
        for x in xrange(2, len(tokens) - 1, 2):
            res[int(tokens[x])] = tokens[x + 1]
            #row.append(tokens[x + 1])
        for key in sorted(res.keys()):
            print key
            row.append(res[key])
        writer.writerow(row)
    outFH.close()
    fh.close()

if __name__ == "__main__":
    import sys
    main(sys.argv[1], sys.argv[2])

#!/usr/bin/env python

import csv
import sys


def main(annotatedFile, objFile, outFile):
    fh = open(annotatedFile)
    reader = csv.reader(fh, delimiter='\t', quoting=csv.QUOTE_NONNUMERIC)
    annotatedSegments = set()
    for row in reader:
        seg = row[0].decode("utf-8")
        annotatedSegments.add(seg)
    fh.close()
    fh = open(objFile)
    reader = csv.reader(fh, delimiter='\t', quoting=csv.QUOTE_NONNUMERIC)
    outFH = open(outFile, 'w')
    writer = csv.writer(outFH, delimiter='\t', quoting=csv.QUOTE_NONNUMERIC)
    for row in reader:
        objSeg = row[0].decode('utf-8')
        if objSeg in annotatedSegments:
            print "Already seen segment '%s', skipping" % objSeg
        else:
            writer.writerow(row)
    fh.close()
    outFH.close()

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])

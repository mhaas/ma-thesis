#!/usr/bin/env python
# -*- coding: utf -*-

import csv
import sys
import codecs


def read_segments(fileName):
    fh = codecs.open(fileName, 'r', 'utf-8')
    # strip because that's what AnnotationToPTB does
    segments = set(map(lambda x: x.strip(), fh.readlines()))
    fh.close()
    return segments


def main(tsvFile, segmentsFile, outFile):
    segments = read_segments(segmentsFile)
    fh = open(tsvFile)
    outFH = open(outFile, 'w')
    reader = csv.reader(fh, delimiter='\t')
    writer = csv.writer(outFH, delimiter='\t', quoting=csv.QUOTE_NONNUMERIC)
    for row in reader:
        segment = row[0].decode('utf-8').strip()
        if segment not in segments:
            print "Invalid segment: '%s'" % segment
        else:
            print row
            writer.writerow([row[0], int(float(row[1]))])
    fh.close()
    outFH.close()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])

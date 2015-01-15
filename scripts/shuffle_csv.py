#!/usr/bin/env python

import csv
import random
import sys


def shuf(inFile, outFile):
    inFH = open(inFile)
    reader = csv.reader(inFH)
    rows = []
    for row in reader:
        rows.append(row)
    inFH.close()
    outFH = open(outFile, 'w')
    writer = csv.writer(outFH)
    random.shuffle(rows)
    for row in rows:
        writer.writerow(row)
    outFH.close()

if __name__ == "__main__":
    shuf(sys.argv[1], sys.argv[2])

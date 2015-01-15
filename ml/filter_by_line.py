#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import sys

# This script reads line numbers from the first row of a CSV file
# and extracts these line from another text file


def get_indices_from_csv(csvFile):
    res = []
    fh = open(csvFile)
    for row in csv.reader(fh):
        res.append(int(row[0]))
    fh.close()
    return res


def main(csvFile, textFile, outFile, limit=None):
    indices = get_indices_from_csv(csvFile)
    fh = open(textFile)
    lines = list(fh.readlines())
    fh.close()
    outFH = open(outFile, "w")
    for index in indices[:limit]:
        outFH.write(lines[index])
    outFH.close()

if __name__ == "__main__":
    if len(sys.argv) == 4:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))

#!/usr/bin/env python

# Given a CSV file produced by the Amazon review downloader,
# simply dump the review text to an output file

import HTMLParser
import sys
import csv


def load_documents(csvFile, outFile):
    outFH = open(outFile, "w")
    h = HTMLParser.HTMLParser()
    fh = open(csvFile)
    reader = csv.reader(fh)
    for row in reader:
        if len(row) < 8 or '<script' in row[8] or '<script' in row[3]:
            print "SKIPPING INVALID ROW"
            continue
       # try:
       ##     label = float(row[3])
       # except ValueError:
       #     print "could not convert label, INVALID ROW"
        #    continue
        # 8 is the review title, 9 is the review text!
        document = h.unescape(row[9].decode("utf-8"))
        outFH.write(document.encode("utf-8"))
        outFH.write('\n')
    fh.close()
    outFH.close()

if __name__ == "__main__":
    load_documents(sys.argv[1], sys.argv[2])

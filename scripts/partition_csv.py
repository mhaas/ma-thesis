#!/usr/bin/python

import sys
import csv

if __name__ == "__main__":
    fh = open(sys.argv[1])
    res = []
    for row in csv.reader(fh):
        res.append(row)

#    for percent in [0.25, 0.50, 0.75, 1.00]:
    for size in [500, 1000, 1500, 2000, 2500, 5000, 10000]:
        cur = res[:size]  # res[:int(percent * (len(res)))]
        out = "data_split_%s" % size
        outFH = open(out, "w")
        w = csv.writer(outFH)
        for curRow in cur:
            w.writerow(curRow)
        outFH.close()

#!/usr/bin/python
# -*- coding: utf-8 -*-

# Converts from tab-separated values back to regular text

import csv
import os
import sys
import glob
import re
import logging

logger = logging.getLogger("fix-tsv")
logging.basicConfig(filename='fix-tsv.log', level=logging.DEBUG)


MMRE = re.compile(ur"(.+),(\d+),(\d+)")


def readMergeMap(mergeMap):
    print mergeMap
    res = {}
    fh = open(mergeMap, "r")
    for line in fh.readlines():
        line = line.decode("utf-8")
        if line.strip() == "":
            logger.debug("line empty, skipping.")
            continue
        match = MMRE.match(line)
        assert match
        fileName = match.group(1) + ".html.txt.split.translated"
        fileName = fileName.strip()
        if not fileName in res:
            res[fileName] = []
        mergeList = res[fileName]
        start = int(match.group(2))
        end = int(match.group(3))
        mergeList.append((start, end))
    # print res
    logger.debug("merge map:")
    logger.debug(res)
    return res


def main(inFile, mergeMapFile):
    if mergeMapFile:
        mergeMap = readMergeMap(mergeMapFile)
    else:
        mergeMap = {}
        logger.debug("mergemap not specified.")
    if os.path.isdir(inFile):
        files = glob.glob(os.path.join(inFile, "*.txt.split.translated"))
    else:
        files = [inFile]
    for f in files:
        # print "Processing file ", f
        fh = open(f, "rb")
        out = open(f + ".fixed", "w")
        r = csv.reader(fh, delimiter="\t")
        r.next()
        buf = []
        for row in r:
            # replace noise
            txt = row[1]
            txt = txt.replace("\xc2\xa0", "")
            buf.append(txt.decode("utf-8").strip())
        mergeList = []
        if os.path.basename(f) in mergeMap:
            mergeList = mergeMap[os.path.basename(f)]
            logger.debug("got mergeList for %s" % f)
        else:
            logger.debug("file not in mergeMap: %s", os.path.basename(f))
        for (start, end) in reversed(mergeList):
            temp = ""
            for index in xrange(start, end + 1):
                logger.debug("Merging %s" % buf[index])
                temp += buf[index]
            for index in xrange(start, end):
                logger.debug("Deleting: %s", buf[index])
                del buf[index]
            buf[start] = temp
        for line in buf:
            out.write(line.encode("utf-8"))
            out.write("\n")
        out.close()
        fh.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Extract translations from TSV files. Optionally merge sentences.')
    parser.add_argument('--input', required=True,
                        help='input file or directory')
    parser.add_argument('--mergemap', required=False, default=None,
                        help='File containing the merge map')

    args = parser.parse_args()
    main(args.input, args.mergemap)

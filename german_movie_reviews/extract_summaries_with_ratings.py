#!/usr/bin/python
# -*- coding: utf-8 -*-

import sample
from collections import OrderedDict
import csv
import yaml
import argparse
import os
import re


def load_ratings_map(ratingsFile):
    fh = open(ratingsFile)
    m = yaml.load(fh)
    fh.close()
    res = {}
    for (name, rating) in m.iteritems():
        name = os.path.basename(name)
        res[name] = rating
    return res


def clean_filename(filename):
    """
    >>> clean_filename('zwei-glorreiche-halunken.html.txt.split')
    'zwei-glorreiche-halunken.html'
    """
    regex = re.compile(ur'^(.*\.html).*$')
    return regex.match(filename).group(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extracts movie summarys'
                                     + ' and movie ratings')
    parser.add_argument('--input', required=True,
                        help='input directory')
    parser.add_argument('--output', required=True,
                        help='output file name for CSV file')
    parser.add_argument('--ratings-map', required=True,
                        help='Map from file name to rating')
    args = parser.parse_args()
    sentences = sample.get_summaries(args.input)
    outFH = open(args.output, "w")
    writer = csv.writer(outFH)
    tmp = OrderedDict()
    m = load_ratings_map(args.ratings_map)
    for s in sentences:
        curFile = clean_filename(s[0])
        if not curFile in tmp:
            tmp[curFile] = []
        tmp[curFile].append(s[2].replace("\n", " "))
    notFound = 0
    invalid = 0
    for (fileName, summaryFragments) in tmp.iteritems():
        if not fileName in m:
            notFound += 1
            continue
        if float(m[fileName]) == -1:
            invalid += 1
            continue
        row = [m[fileName], " ".join(summaryFragments)]
        writer.writerow(row)
    outFH.close()
    print "not found: %s" % notFound
    print "invalid: %s" % invalid

#!/usr/bin/python2
# -*- coding: utf -*-

# Given the meta files for the movie reviews,
# this script produces a sorted list.

import glob
import os
import collections
import argparse
import yaml

def listFiles(directory):
    pattern = "*.html.meta"
    # python 2.7
    res = {}
    for fileName in glob.iglob(os.path.join(directory, pattern)):
        fh = open(fileName, "r")
        # can't use safe_load because of embedded unicode objects
        #metaObj = yaml.safe_load(fh)
        metaObj = yaml.load(fh)
        fh.close()
        if metaObj["rating"] == -1.0:
            print "rating is: %s" % metaObj["rating"]
            print "ratingText is: %s" % metaObj["ratingText"]
        res[fileName[0:-1 * len(".meta")]] = metaObj["rating"]
    res = collections.OrderedDict(reversed(sorted(res.items(), key=lambda t: t[1])))
    return res

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Extracts mapping of file name to movie rating.')
    parser.add_argument('--input', required=True,
                    help='input directory')
    parser.add_argument('--output', required=True,
                    help='output file name for YAML dump')


    args = parser.parse_args()

    r = listFiles(args.input)
    fh = open(args.output, "w")
    yaml.dump(r, fh)
    fh.close()
        


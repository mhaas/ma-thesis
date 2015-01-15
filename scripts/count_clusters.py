#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from apply_cluster_to_ptb import read_cluster
import os


def count(clusterFile):
    dictionary = read_cluster(clusterFile)
    clusterCount = len(set(dictionary.values()))
    fileName = os.path.basename(clusterFile)
    print "%s: %s" % (fileName, clusterCount)


if __name__ == "__main__":
    count(sys.argv[1])

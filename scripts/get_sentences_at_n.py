#!/usr/bin/env python
# -*- coding: utf-8 -*-

from shared import ma_util
import sys


def main(fileName, n):
    trees = ma_util.readPenn(fileName)
    for tree in trees:
        if len(tree.leaves()) >= n:
            print "Sentiment: %s" % tree.node
            print map(lambda x: x.encode('utf-8'), tree.leaves())

if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]))

#!/usr/bin/python
# -*- coding: utf-8 -*-

import nltk.tree
import sys


def ptbToTree(ptbFile):
    fh = open(ptbFile)
    t = fh.read()
    fh.close()
    tree = nltk.tree.Tree(t)
    return tree


def main(tigerFile):
    tree = ptbToTree(tigerFile)
    tree.draw()

if __name__ == "__main__":
    main(sys.argv[1])

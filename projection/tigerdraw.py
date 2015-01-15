#!/usr/bin/python
# -*- coding: utf-8 -*-

import shared.ma_util
import project
import sys


def main(tigerFile):
    tree = project.tigerToTree(tigerFile)
    res = []
    for foo in shared.ma_util.walkTree(tree):
        res.append(foo.node)
    print res
    tree.draw()

if __name__ == "__main__":
    main(sys.argv[1])

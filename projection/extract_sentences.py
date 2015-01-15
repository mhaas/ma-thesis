#!/usr/bin/python
# -*- coding: utf-8 -*-

import tigerhelper as th
from lxml import etree
import sys


def main(tigerFile, sentenceList, out):
    tigerXML = th.TigerHelper(tigerFile)
    res = []
    for sID in sentenceList.split(","):
        sentenceNode = tigerXML.getSentence(sID)
        assert sentenceNode is not None
        res.append(sentenceNode)
    print res
    result = th.constructTigerXML(res)
    etree.ElementTree(result).write(out)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])

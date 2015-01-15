# -*- coding: utf-8 -*-

import unittest
import yaml
import project
import tempfile
from lxml import etree
import itertools
import logging
import tigerhelper as th
from tigerhelper import TigerHelper
import shared.ma_util

logger = logging.Logger("test-project")
logging.basicConfig(filename="test-project.log",
                    level=logging.DEBUG)


class TestMappingExtractor(unittest.TestCase):

    def _mapToString(self, mapping):
        newMap = {}
        for (key, value) in mapping.iteritems():
            newMap[str(key)] = str(value)
        return newMap

    def test2(self):
        inputFile = "tests/1.xml"
        inputFile = th.collapseToTmp(inputFile)
        print "Unary-collapsed tree at %s" % inputFile
        self.maxDiff = None
        penn = shared.ma_util.readPenn("tests/1-binarization-yv.ptb").next()
        tiger = project.readTiger(inputFile).next()
        res = project.getMappingFromNodeIDToSentiment(tiger, penn)
        expected = yaml.load(open("tests/1.newcollapse.expected.yml"))
        self.assertEqual(self._mapToString(res), self._mapToString(expected))


class TestProjection(unittest.TestCase):

    def compareXML(self, origFile, newFileFH):
        origXML = etree.parse(open(origFile))
        newXML = etree.parse(newFileFH)
        # traverse in document order
        for (origNode, newNode) in itertools.izip_longest(
                origXML.iter(),
                newXML.iter(),
                fillvalue="LIST_LENGTH_NOT_EQUAL"):
            self.assertEqual(etree.tostring(origNode), etree.tostring(newNode))

    def compareSentences(self, origFile, newFileFH):
        origXML = TigerHelper(origFile)
        newXML = TigerHelper(newFileFH)
        origSentence = origXML.tree.find(".//s")
        newSentence = newXML.tree.find(".//s")
        for (origNode, newNode) in itertools.izip_longest(
                origXML.preOrder(origSentence),
                newXML.preOrder(newSentence),
                fillvalue="LIST_LENGTH_NOT_EQUAL"):
            self.assertEqual(origNode, newNode)

    def compareTrees(self, origFile, newFileFH):
        origXML = project.readTiger(origFile).next()
        newXML = project.readTiger(newFileFH).next()
        origTree = project.tigerToTree(origXML)
        newTree = project.tigerToTree(newXML)
        # get sentences from xml
        for (origNode, newNode) in itertools.izip_longest(
                shared.ma_util.walkTree(origTree),
                shared.ma_util.walkTree(newTree),
                fillvalue="LIST_LENGTH_NOT_EQUAL"):
            print "comparing: %s, %s" % (origNode, newNode)
            print "comparing values: %s, %s" % (origNode.node, newNode.node)
            self.assertEqual(origNode, newNode)
            self.assertEqual(origNode.node, newNode.node)

    def test1(self):
        outFH = tempfile.TemporaryFile()
        source = "tests/1.xml"
        target = "tests/2-target.xml"
        alignment = "tests/2-align.xml"
        annotations = "tests/2-sentiment.ptb"
        project.main(source,
                     annotations,
                     alignment,
                     target,
                     outFH,
                     True,
                     False,
                     False,
                     ['good', 'fuzzy'])
        outFH.seek(0)
        #self.compareXML("tests/2-mapped.xml", outFH)
        #this only compares node ids!
        #self.compareTrees("tests/2-mapped.xml", outFH)
        self.compareSentences("tests/2-mapped.xml", outFH)

    def testReadTiger(self):
        count = 0
        for sentence in project.readTiger(open("tests/1.xml")):
            count += 1
        self.assertEqual(count, 1)

    def testRootProjection(self):
        """This test tests the root projection. Root labels
        are projected from source to target if the target root does not
        have a valid sentiment label.
        """
        outFH = tempfile.TemporaryFile()
        source = "tests/1.xml"
        target = "tests/2-target.xml"
        alignment = "tests/3-align.xml"
        annotations = "tests/2-sentiment.ptb"
        project.main(source,
                     annotations,
                     alignment,
                     target,
                     outFH,
                     True,
                     False,
                     True,
                     ['good', 'fuzzy'])
        outFH.seek(0)
        #self.compareXML("tests/2-mapped.xml", outFH)
        #this only compares node ids!
        #self.compareTrees("tests/2-mapped.xml", outFH)
        self.compareSentences("tests/3-mapped.xml", outFH)

# -*- coding: utf-8 -*-

import unittest
import tigerhelper as th
from lxml import etree
import itertools
import tempfile


class TestTigerHelper(unittest.TestCase):

    def testGetParent(self):
        self.maxDiff = None
        tigerXML = th.TigerHelper("tests/1.xml")
        sentenceFragment = tigerXML.tree.find(".//s")
        parent = th.getParent("126_7",
                              sentenceFragment)
        self.assertEquals(parent.get("id"), "s126_n500BIN")

    def testPreOrder(self):
        self.maxDiff = None
        tigerXML = th.TigerHelper("tests/1.xml")
        res = []
        for node in tigerXML.preOrder(tigerXML.tree.find('.//s')):
            res.append(node)
        ids = map(lambda x: x[0], res)
        expected = [
            's126_VROOT', '126_501', 's126_n505BIN', 's126_n502BIN', '126_502',
            '126_3', 's126_n501BIN', '126_4', '126_505', '126_6',
            's126_n500BIN', '126_7', '126_8', '126_509', 's126_n503BIN',
            '126_10', '126_511', '126_12', '126_513', '126_514', '126_15',
            '126_516', '126_17', '126_518', 's126_n504BIN', '126_19', '126_20',
            '126_521', '126_22', '126_523', '126_24', '126_25', '126_26']
        self.assertTrue(len(res) > 0)
        self.assertEqual(ids, expected)

    def testApplyParentSentiment(self):
        tigerXML = th.TigerHelper("tests/2.xml")
        sentiment = th.getSentiment(tigerXML.getNode("126_4"))
        self.assertEqual(sentiment, None)
        tigerXML.applyParentSentimentValue()
        sentiment = th.getSentiment(tigerXML.getNode("126_4"))
        self.assertEqual(sentiment, "0")

    def compareSentences(self, origFile, newFileFH):
        origXML = th.TigerHelper(origFile)
        newXML = th.TigerHelper(newFileFH)
        origSentence = origXML.tree.find(".//s")
        newSentence = newXML.tree.find(".//s")
        for (origNode, newNode) in itertools.izip_longest(
                origXML.preOrder(origSentence),
                newXML.preOrder(newSentence),
                fillvalue="LIST_LENGTH_NOT_EQUAL"):
            self.assertEqual(origNode, newNode)

    def testCollapseUnaryParent(self):
        # this method tests the case where we want to keep the parent
        outFH = tempfile.TemporaryFile()
        tigerXML = th.TigerHelper("tests/3.xml")
        tigerXML.collapseUnary(collapseConsecutive=False)
        outFH.write(etree.tostring(tigerXML.tree).encode("utf-8"))
        outFH.seek(0)
        self.compareSentences("tests/3-collapsed.xml", outFH)

    def testCollapseUnaryChild(self):
        # this method tests the case where we want to keep the child
        # as an added bonus, this tests the case where we remove the graph
        # root.
        outFH = tempfile.TemporaryFile()
        tigerXML = th.TigerHelper("tests/4.xml")
        tigerXML.collapseUnary(collapseConsecutive=False)
        outFH.write(etree.tostring(tigerXML.tree).encode("utf-8"))
        outFH.seek(0)
        self.compareSentences("tests/4-collapsed.xml", outFH)

    def testCollapseUnaryParentLeaf(self):
        # this method tests the case where we want to keep the parent
        # here, we collapse a leaf.
        outFH = tempfile.TemporaryFile()
        tigerXML = th.TigerHelper(open("tests/5.xml"))
        tigerXML.collapseUnary()
        outFH.write(etree.tostring(tigerXML.tree).encode("utf-8"))
        outFH.seek(0)
        # The old code used to collapse the terminal into the
        # non-terminal, resulting in a dangling non-terminal
        # since this does not make much sense, we
        # special-case for that and always collapse an NT into a T
        self.compareSentences("tests/5-collapsed.xml", outFH)

    def testCollapseUnaryChildLeaf(self):
        # this method tests the case where we want to keep the child
        # here, we collapse the parent of a leaf.
        outFH = tempfile.TemporaryFile()
        tigerXML = th.TigerHelper("tests/6.xml")
        tigerXML.collapseUnary()
        outFH.write(etree.tostring(tigerXML.tree).encode("utf-8"))
        outFH.seek(0)
        self.compareSentences("tests/6-collapsed.xml", outFH)

    def testCollapseUnaryExcept(self):
        outFH = tempfile.TemporaryFile()
        tigerXML = th.TigerHelper("tests/7.xml")
        tigerXML.collapseUnaryExcept([], collapseConsecutive=False)
        outFH.write(etree.tostring(tigerXML.tree).encode("utf-8"))
        outFH.seek(0)
        self.compareSentences("tests/7-collapsed.xml", outFH)

    def testCollapseUnaryExcept1(self):
        outFH = tempfile.TemporaryFile()
        tigerXML = th.TigerHelper("tests/7.xml")
        # this node would be removed anyways
        # almost same test as the one before
        tigerXML.collapseUnaryExcept(["126_100"],
                                     collapseConsecutive=False)
        outFH.write(etree.tostring(tigerXML.tree).encode("utf-8"))
        outFH.seek(0)
        self.compareSentences("tests/7-collapsed.xml", outFH)

    def testCollapseUnaryExcept2(self):
        outFH = tempfile.TemporaryFile()
        tigerXML = th.TigerHelper("tests/7.xml")
        # we always prefer the child nodes if both nodes are
        # candidates for collapse
        tigerXML.collapseUnaryExcept(["s126_VROOT", "126_100"],
                                     collapseConsecutive=False)
        outFH.write(etree.tostring(tigerXML.tree).encode("utf-8"))
        outFH.seek(0)
        self.compareSentences("tests/7-collapsed.xml", outFH)

    def testCollapseUnaryExcept3(self):
        outFH = tempfile.TemporaryFile()
        tigerXML = th.TigerHelper("tests/7.xml")
        # we always prefer the child nodes if both nodes are
        # candidates for collapse
        tigerXML.collapseUnaryExcept(["s126_VROOT"],
                                     collapseConsecutive=False)
        outFH.write(etree.tostring(tigerXML.tree).encode("utf-8"))
        outFH.seek(0)
        self.compareSentences("tests/8-collapsed.xml", outFH)

    def testCollapseUnaryConsecutive(self):
        outFH = tempfile.TemporaryFile()
        tigerXML = th.TigerHelper(open("tests/3.xml"))
        tigerXML.collapseUnary(collapseConsecutive=True)
        outFH.write(etree.tostring(tigerXML.tree).encode("utf-8"))
        outFH.seek(0)
        self.compareSentences("tests/3-collapsed-consecutive.xml", outFH)

    # the whole consecutive code is a bit undertested,
    # e.g. with regards to the correct traversal order
    def testCollapseUnaryConsecutiveExcept(self):
        outFH = tempfile.TemporaryFile()
        tigerXML = th.TigerHelper(open("tests/7.xml"))
        # we always prefer the child nodes if both nodes are
        # candidates for collapse
        tigerXML.collapseUnaryExcept(["s126_VROOT"])
        outFH.write(etree.tostring(tigerXML.tree).encode("utf-8"))
        outFH.seek(0)
        self.compareSentences("tests/7-consecutive.xml", outFH)

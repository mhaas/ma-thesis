# -*- coding: utf-8 -*-

import unittest
import evaluate
from ma_util import NEG, NEU, POS
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score


class TestEvaluate(unittest.TestCase):

    def test_tree_reading(self):
        (root, node) = evaluate.getCoarseGrainedTreeLabelsFile(
            'tests/ptb/small_treebank.ptb')
        expectedRoot = [NEU, NEG, NEU, NEU]
        expectedLabels = [NEU, NEG, POS, POS, POS, NEG, POS]
        expectedLabels += [NEG, NEU, POS, POS, POS, NEU, NEG]
        expectedLabels += [NEU, NEG, POS, POS, POS, NEG, POS]
        expectedLabels += [NEU, NEG, POS, POS, POS, NEG, POS]
        self.assertSequenceEqual(root, expectedRoot)
        self.assertSequenceEqual(node, expectedLabels)

    def test_moreStats(self):
        print "Running test"
        goldLabels = [0, 0, 0, 0, 1, 1, 2, 2, 2]
        predictedLabels = [0, 0, 0, 1, 1, 2, 1, 2, 1]
        # Confusion Matrix
        #   0   1   2
        # 0 3   1   0
        # 1 0   1   1
        # 2 0   2   1
        # tp0: 3
        # fp0: 0
        # fn0: 1
        # tn0: 5
        myAcc0 = (3.0 + 5) / (3 + 5 + 0 + 1)
        # TODO: do the rest of these
        (p0, r0, fm0, acc0) = evaluate.moreStats(
            goldLabels, predictedLabels, 0)
        self.assertEquals(acc0, myAcc0)
        (p1, r1, fm1, acc1) = evaluate.moreStats(
            goldLabels, predictedLabels, 1)
        (p2, r2, fm2, acc2) = evaluate.moreStats(
            goldLabels, predictedLabels, 2)
        f1s = f1_score(goldLabels, predictedLabels, average=None)
        self.assertEquals(f1s[0], fm0)
        self.assertEquals(f1s[1], fm1)
        self.assertEquals(f1s[2], fm2)
        precs = precision_score(goldLabels, predictedLabels, average=None)
        self.assertEquals(precs[0], p0)
        self.assertEquals(precs[1], p1)
        self.assertEquals(precs[2], p2)
        recs = recall_score(goldLabels, predictedLabels, average=None)
        self.assertEquals(recs[0], r0)
        self.assertEquals(recs[1], r1)
        self.assertEquals(recs[2], r2)
        # no test for accuracy now - sklearn does not have a method for that

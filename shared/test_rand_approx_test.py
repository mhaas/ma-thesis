# -*- coding: utf-8 -*-

import unittest
import rand_approx_test as rat
import nltk
import evaluate
import random
import ma_util
import sklearn


class TestRandApproxTest(unittest.TestCase):

    def setUp(self):
        self.tree1 = nltk.tree.Tree(
            '(2 (1 (3 foo) (4 bar)) (3 (1 baz) (3 qux)))')
        self.tree2 = nltk.tree.Tree(
            '(0 (0 (0 foo) (0 bar)) (0 (0 baz) (0 qux)))')
        print self.tree1
        print self.tree2
        self.tree1L = evaluate.getTreeLabels(
            [self.tree1], ma_util.GRANULARITY_FINE)
        self.tree2L = evaluate.getTreeLabels(
            [self.tree2], ma_util.GRANULARITY_FINE)
        # I use nodeF1Statistic, but the tests have been developed with
        # accuracy_score.
        #self.measure = rat.nodeF1Statistic
        self.measure = sklearn.metrics.accuracy_score
        self.randomTree1 = self.generate_random_tree(5)
        self.randomTree2 = self.generate_random_tree(5)
        self.randomTree1L = evaluate.getTreeLabels(
            [self.randomTree1], ma_util.GRANULARITY_FINE)
        self.randomTree2L = evaluate.getTreeLabels(
            [self.randomTree2], ma_util.GRANULARITY_FINE)

    @staticmethod
    def generate_random_tree(depth):
        if depth == 0:
            raise ValueError("Invalid depth %s" % depth)
        if depth == 1:
            t = nltk.tree.Tree('('
                               + TestRandApproxTest._generate_random_label()
                               + ' Leaf)')
            return t
        tree = nltk.tree.Tree(TestRandApproxTest._generate_random_label(), [])
        # binary recursion. It has been a while.
        leftChild = TestRandApproxTest.generate_random_tree(depth - 1)
        rightChild = TestRandApproxTest.generate_random_tree(depth - 1)
        tree.append(leftChild)
        tree.append(rightChild)
        return tree

    @staticmethod
    def _generate_random_label():
        return random.choice(['0', '1', '2', '3', '4'])

    def test_no_significance1(self):
        val = rat.approximate_randomization_test(self.tree1L,
                                                 self.tree1L,
                                                 self.tree1L,
                                                 self.measure,
                                                 0.01)
        self.assertFalse(val)

    def test_significance2(self):
        # the significance level estimated here is approx 0.5!
        # needs more data for more significance, I suppose.
        val = rat.approximate_randomization_test(self.tree1L,
                                                 self.tree1L,
                                                 self.tree2L,
                                                 self.measure,
                                                 0.6)
        self.assertTrue(val)

    def test_no_significance2(self):
        # this test uses random trees, so it occasionally fails...
        val = rat.approximate_randomization_test(self.randomTree1L,
                                                 self.randomTree1L,
                                                 self.randomTree2L,
                                                 self.measure,
                                                 0.01)
        self.assertFalse(val)

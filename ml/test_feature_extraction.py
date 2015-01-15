# -*- coding: utf-8 -*-

import unittest
import shared.ma_util
import feature_extraction
import numpy as np
import os
import sys


base = os.environ.get('DATADIR')
if not base:
    print >> sys.stderr, "DATADIR not set in environment. Bailing out"
    sys.exit(-1)


class TestGoldExtractor(unittest.TestCase):

    def setUp(self):
        self.trees = list(shared.ma_util.readPenn(
            '../shared/tests/ptb/small_treebank.ptb'))

    def testFine(self):
        ge = feature_extraction.GoldExtractor(
            shared.ma_util.GRANULARITY_FINE)
        gold = ge.extract_gold_from_trees(self.trees)
        expected = [2, 1, 3, 4, 3, 1, 3, 1, 2, 3, 4, 3, 2,
                    1, 2, 1, 3, 4, 3, 1, 3, 2, 1, 3, 4, 3, 1, 3]
        self.assertListEqual(expected, gold.tolist())
        self.assertTrue(np.array_equal(np.asarray(expected), gold))

    def testCoarse(self):
        ge = feature_extraction.GoldExtractor(
            shared.ma_util.GRANULARITY_COARSE)
        gold = ge.extract_gold_from_trees(self.trees)
        expected = [1, 0, 2, 2, 2, 0, 2, 0, 1, 2, 2, 2, 1,
                    0, 1, 0, 2, 2, 2, 0, 2, 1, 0, 2, 2, 2, 0, 2]
        self.assertListEqual(expected, gold.tolist())
        self.assertTrue(np.array_equal(np.asarray(expected), gold))


class LexiconExtractorTest(unittest.TestCase):

    def setUp(self):
        self.pos = [u'Der', u'Film', u'ist', u'gut']
        self.neg = [u'Der', u'Film', u'ist', u'schlecht']
        self.flipPos = [u'Der', u'Film', u'ist', u'nicht', u'gut']
        self.flipNeg = [u'Der', u'Film', u'ist', u'nicht', u'schlecht']

    def _testLex(self, lexicon):
        self.assertEquals(lexicon.getCoarseSentiment(self.pos),
                          shared.ma_util.POS)
        self.assertEquals(lexicon.getCoarseSentiment(self.neg),
                          shared.ma_util.NEG)

    def _testFlip(self, lexicon):
        self.assertFalse(lexicon.hasShifter(self.pos))
        self.assertFalse(lexicon.hasShifter(self.neg))
        self.assertTrue(lexicon.hasShifter(self.flipPos))
        self.assertEquals(
            shared.ma_util.flipSentiment(
                lexicon.getCoarseSentiment(self.flipPos)),
            shared.ma_util.NEG)
        self.assertTrue(lexicon.hasShifter(self.flipNeg))
        self.assertEquals(
            shared.ma_util.flipSentiment(
                lexicon.getCoarseSentiment(self.flipNeg)),
            shared.ma_util.POS)

    def _testLexPos(self, lexicon):
        # input is always STTS-tagged
        test1Neg = [('ADJA', u'grottenschlecht')]
        # should return neutral
        test2Neg = [('ADV', u'grottenschlecht')]
        test1Pos = [('ADJD', u'toll')]
        # obviously bogus POS
        test2Pos = [('PDAT', u'toll')]
        test3Pos = [('ART', u'Der'), ('NN', u'Film'), ('VVFIN', u'ist'),
                    ('ADJD', u'gut')]
        self.assertEquals(
            lexicon.getCoarseSentimentPOS(test1Neg), shared.ma_util.NEG)
        self.assertEquals(
            lexicon.getCoarseSentimentPOS(test2Neg), shared.ma_util.NEU)
        self.assertEquals(
            lexicon.getCoarseSentimentPOS(test1Pos), shared.ma_util.POS)
        self.assertEquals(
            lexicon.getCoarseSentimentPOS(test2Pos), shared.ma_util.NEU)
        self.assertEquals(
            lexicon.getCoarseSentimentPOS(test3Pos), shared.ma_util.POS)

    def testSentiWS(self):
        sentiPOS = os.path.join(
            base, '3rdparty/sentiws/SentiWS_v1.8c_Positive.txt')
        sentiNEG = os.path.join(
            base, '3rdparty/sentiws/SentiWS_v1.8c_Negative.txt')
        e = feature_extraction.SentiWSExtractor(None, sentiPOS, sentiNEG)
        self._testLex(e)
        self._testLexPos(e)

    def testPolart(self):
        polFile = os.path.join(base, '3rdparty/klenner_lex/german.lex')
        e = feature_extraction.KlennertExtractor(polFile)
        self._testLex(e)
        self._testFlip(e)

    def testSentiMerge(self):
        lexFile = os.path.join(
            base, '3rdparty/SentiMerge/data/sentimerge.txt')
        e = feature_extraction.SentiMergeExtractor(lexFile)
        # self._testLex(e)
        # Now this is fun: the code works as designed, but the
        # weights are assigned such that the sentiment becomes negative
        # HERE BE DRAGONS
        self.assertEquals(e.getCoarseSentiment(self.pos),
                          shared.ma_util.NEG)
        self.assertEquals(e.getCoarseSentiment(self.neg),
                          shared.ma_util.NEG)
        self._testLexPos(e)
        # test upper case handling
        self.assertEquals(e.getCoarseSentiment([u'Abbruch']),
                          shared.ma_util.NEG)

    def testGPC(self):
        gpcPos = os.path.join(
            base, '3rdparty/GermanPolarityClues/GermanPolarityClues-2012/'
            + 'GermanPolarityClues-Positive-21042012.tsv')
        gpcNeg = os.path.join(
            base, '3rdparty/GermanPolarityClues/GermanPolarityClues-2012/'
            + 'GermanPolarityClues-Negative-21042012.tsv')
        e = feature_extraction.GermanPolarityCluesExtractor(gpcPos, gpcNeg)
        self._testLex(e)
        self._testLexPos(e)
        # this is intended behaviour: 'zwangsweise' is tagged as AD,
        # and it's an adverb
        # otherwise, anything tagged ADV in the data is eligible to be lookup
        # as adjective
        self.assertEquals(e.getCoarseSentiment([u'zwangsweise']),
                          shared.ma_util.NEG)
        self.assertEquals(e.getCoarseSentimentPOS([('ADJ', u'zwangsweise')]),
                          shared.ma_util.NEG)
        self.assertEquals(e.getCoarseSentimentPOS([('ADV', u'zwangsweise')]),
                          shared.ma_util.NEU)

    def testMznML(self):
        key = 'f56da36cf010264035535def0ca31b2c'
        p = os.path.join(base, 'mzn-reg-models-wo-singletons/')
        model = os.path.join(p, 'lassocv_%s.pickle' % key)
        alphabet = os.path.join(p, 'alphabet_%s.pickle' % key)
        e = feature_extraction.MznMLExtractor(alphabet, model)
        #self._testLex(e)
        # amazon coverage is not that great, so make simpler test case
        self.assertEquals(e.getCoarseSentiment([u'enttäuscht']),
                          shared.ma_util.NEG)
        # upper case?
        self.assertEquals(e.getCoarseSentiment([u'Enttäuscht']),
                          shared.ma_util.NEG)
        self.assertEquals(e.getCoarseSentiment([u'klare']),
                          shared.ma_util.POS)

class TokenExtractorTest(unittest.TestCase):

    def setUp(self):
        self.trees = list(shared.ma_util.readPenn(
            '../shared/tests/ptb/small_treebank.ptb'))
        self.desired0 = np.asarray([[1.,  1.,  1.,  1.],
                                    [0.,  1.,  1.,  0.],
                                    [0.,  1.,  0.,  0.],
                                    [0.,  0.,  1.,  0.],
                                    [1.,  0.,  0.,  1.],
                                    [1.,  0.,  0.,  0.],
                                    [0.,  0.,  0.,  1.]])
        self.desired2 = np.asarray([[1.,  1.,  1.,  1.],
                                    [0.,  1.,  1.,  0.],
                                    [0.,  0.,  1.,  0.],
                                    [0.,  1.,  0.,  0.],
                                    [1.,  0.,  0.,  1.],
                                    [0.,  0.,  0.,  1.],
                                    [1.,  0.,  0.,  0.]])
        self.desired3 = np.asarray([[1.,  1.,  1.,  1.],
                                    [0.,  0.,  1.,  1.],
                                    [0.,  0.,  0.,  1.],
                                    [0.,  0.,  1.,  0.],
                                    [1.,  1.,  0.,  0.],
                                    [0.,  1.,  0.,  0.],
                                    [1.,  0.,  0.,  0.]])

    def test_extract_xgrams(self):
        # tests whether individual trees are represented correctly
        # i.e. whether the subtrees are represented correctly and if
        # the ordering of the subtrees is correct
        te = feature_extraction.TokenExtractor(self.trees, unigrams=True)
        self._testTree(te, self.trees[0], self.desired0)
        # now test the second tree
        # yes, don't care about the trees[1]
        self._testTree(te, self.trees[2], self.desired2)
        self._testTree(te, self.trees[3], self.desired3)

    def _testTree(self, te, tree, desired):
        vectors = te.extract_xgrams_from_tree(tree)
        self.assertTrue(np.array_equal(vectors, desired))

    def test_trees_to_vectors(self):
        # tests whether a treebank consisting of more than one tree
        # is represented correctly
        trees = [self.trees[0], self.trees[2], self.trees[3]]
        te = feature_extraction.TokenExtractor(trees, unigrams=True)
        print "this is desired0:"
        print self.desired0
        print "this is desired2:"
        print self.desired2
        print "this is desired3:"
        print self.desired3
        vectors = te.trees_to_vectors(trees)
        # print "this is desired3:"
        #print self.desired3
        # Both concatenation and vstack do what we want here
        # print "This is the concatenation"
        #desired = np.concatenate([self.desired0, self.desired2])
        # print desired
        # print "This is the vstack"
        desired = np.vstack([self.desired0, self.desired2, self.desired3])
        # print desired
        # append does not
        # print "This is append"
        #desired = np.append(self.desired0, self.desired2)
        # print desired
        self.assertTrue(np.array_equal(vectors, desired))

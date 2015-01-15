#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is a naive implementation of a sentiment analysis system
# based on SentiWS.
# The naivety is in contrast to earlier, machine learning based
# systems which were more sophisticated.
# The goal is to have identical classification mechanisms where only
# the underlying lexicon is changed.
# This facilitates a fair comparison between the SentiWS
# and the learned, regression-based lexicon

from ml.ensemble import EnsembleLearner
# TODO: this should be refactored
# And all eval-related code go into separate module
import shared.ma_util
import argparse
import os
import sys

from ml.feature_extraction import KlennertExtractor, SentiWSExtractor
from ml.feature_extraction import SentiMergeExtractor
from ml.feature_extraction import GermanPolarityCluesExtractor
from ml.feature_extraction import MznMLExtractor
SENTIWS = "SentiWS"
POLART = "PolArt"
SENTIMERGES = "SentiMergeSilly"
SENTIMERGEP = "SentiMergePrecision"
SENTIMERGER = "SentiMergeRecall"
GPC = "GermanPolarityClues"
MZNL = "MznLasso"
MZNSVR = 'MznSVR'

class NaivePredictor(object):

    def __init__(self, extractor, shiftFinder=None):
        self.e = extractor
        self.sf = shiftFinder

    def predictWithPOS(self, parseFile, treesFile):
        parseTrees = list(shared.ma_util.readPenn(parseFile))
        predictedLabels = []
        for parseSentence in parseTrees:
            for parseNode in shared.ma_util.walkTree(parseSentence):
                posTags = parseNode.pos()
                # reverse tuple order
                posTags = map(lambda (a, b): (b, a), posTags)
                predictedSentiment = e.getCoarseSentimentPOS(posTags)
                # We do not always look for shifters
                if self.sf and self.sf.hasShifter(parseNode.leaves()):
                    predictedSentiment = shared.ma_util.flipSentiment(
                        predictedSentiment)
                predictedLabels.append(predictedSentiment)
        if treesFile:
            self.serialize_trees(parseTrees, predictedLabels, treesFile)

    def predict(self, goldFile, treesFile):
        goldTrees = list(shared.ma_util.readPenn(goldFile))
        predictedLabels = []
        for goldSentence in goldTrees:
            for goldNode in shared.ma_util.walkTree(goldSentence):
                predictedSentiment = e.getCoarseSentiment(goldNode.leaves())
                # We do not always look for shifters
                if self.sf and self.sf.hasShifter(goldNode.leaves()):
                    predictedSentiment = shared.ma_util.flipSentiment(
                        predictedSentiment)
                predictedLabels.append(predictedSentiment)
        if treesFile:
            self.serialize_trees(goldTrees, predictedLabels, treesFile)

    @staticmethod
    def serialize_trees(trees, predictions, outFile):
        newTrees = EnsembleLearner.apply_prediction_to_tree(trees, predictions,
                                                            predGranularity=shared.ma_util.GRANULARITY_COARSE)
        shared.ma_util.serializeTrees(newTrees, outFile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Assign labels to tree nodes')
    parser.add_argument('--parse', required=True,
                        help='PTB file on which to apply labels')
    parser.add_argument('--predicted-trees-file', required=False,
                        help='Serialize predicted trees to file (PTB).')
    parser.add_argument('--lexicon', required=True,
                        choices=[SENTIWS, MZNL, MZNSVR],
                        help='Which Lexicon to use')
    parser.add_argument('--shift-finder', required=False,
                        choices=[POLART],
                        help='Which lexicon to use for shifters')
    parser.add_argument('--pos-mode', required=False,
                        action='store_true',
                        help='Use POS-informed word lookup. Provide parse tree!')
    args = parser.parse_args()
    base = os.environ.get('DATADIR')
    if not base:
        print >> sys.stderr, "DATADIR not set in environment. Bailing out"
        sys.exit(-1)
    senMLexFile = os.path.join(base,
                               '3rdparty/SentiMerge/data/sentimerge.txt')
    polFile = os.path.join(base, '3rdparty/klenner_lex/german.lex')
    if args.lexicon == POLART:
        e = KlennertExtractor(polFile)
    elif args.lexicon == SENTIWS:
        sentiPOS = os.path.join(
            base, '3rdparty/sentiws/SentiWS_v1.8c_Positive.txt')
        sentiNEG = os.path.join(
            base, '3rdparty/sentiws/SentiWS_v1.8c_Negative.txt')
        e = SentiWSExtractor(None, sentiPOS, sentiNEG)
    elif args.lexicon == SENTIMERGES:
        e = SentiMergeExtractor(senMLexFile,
                                threshold=SentiMergeExtractor.SILLY_THRESHOLD)
    elif args.lexicon == SENTIMERGEP:
        e = SentiMergeExtractor(senMLexFile,
                                threshold=SentiMergeExtractor.PRECISION_THRESHOLD)
    elif args.lexicon == SENTIMERGER:
        e = SentiMergeExtractor(senMLexFile,
                                threshold=SentiMergeExtractor.RECALL_THRESHOLD)
    elif args.lexicon == GPC:
        gpcPos = os.path.join(
            base, '3rdparty/GermanPolarityClues/GermanPolarityClues-2012/'
            + 'GermanPolarityClues-Positive-21042012.tsv')
        gpcNeg = os.path.join(
            base, '3rdparty/GermanPolarityClues/GermanPolarityClues-2012/'
            + 'GermanPolarityClues-Negative-21042012.tsv')
        e = GermanPolarityCluesExtractor(gpcPos, gpcNeg)
    elif args.lexicon == MZNL:
        key = 'f56da36cf010264035535def0ca31b2c'
        p = os.path.join(base, 'mzn-reg-models-wo-singletons/')
        model = os.path.join(p, 'lassocv_%s.pickle' % key)
        alphabet = os.path.join(p, 'alphabet_%s.pickle' % key)
        e = MznMLExtractor(alphabet, model)
    elif args.lexicon == MZNSVR:
        key = '98502e780025bfe34b47972e23dc13d6'
        p = os.path.join(base, 'mzn-reg-models-wo-singletons-linsvr/')
        model = os.path.join(p, 'linsvr_%s.pickle' % key)
        alphabet = os.path.join(p, 'alphabet_%s.pickle' % key)
        e = MznMLExtractor(alphabet, model)
    if args.shift_finder == POLART:
        sf = KlennertExtractor(polFile)
    else:
        sf = None
    p = NaivePredictor(e, sf)
    if args.pos_mode:
        p.predictWithPOS(args.parse, args.predicted_trees_file)
    else:
        p.predict(args.parse, args.predicted_trees_file)

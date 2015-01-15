#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script computes a sentiment score for
a phrase given a coefficient vector and an alphabet.
"""

from learn_mzn_review_score import MznRegression


# can't use cPickle, fails when loading large pickles.
# http://bugs.python.org/issue13555
#import cPickle as pickle
import pickle
import argparse
import shared.evaluate
import shared.ma_util
#from sklearn import svm
import csv
import itertools
import logging

logger = logging.getLogger("evaluate_coef_sentiment_prediction")


class PhrasePredictor(object):

    def __init__(self, alphabet, model, args, dump_csv_file):
        self.alphabet_file = alphabet
        self.model_file = model
        self.args_file = args
        self.dump_csv_file = dump_csv_file
        self.loadData()

    def loadGoldTrees(self, goldFile):
        self.goldTrees = list(shared.ma_util.readPenn(goldFile))

    def loadData(self):
        self.alphabet = pickle.load(open(self.alphabet_file))
        self.model = pickle.load(open(self.model_file))
        self.args = pickle.load(open(self.args_file))
        if not hasattr(self.model, "coef_"):
            self.coef_vector = self.model.scores_
        else:
            self.coef_vector = self.model.coef_
        # some classifiers provide one vector per class
        if len(self.coef_vector) == 1:
            self.coef_vector = self.coef_vector[0]
        self.reverse_alphabet = {}
        for token, index in self.alphabet.iteritems():
            self.reverse_alphabet[index] = token
        self.helper = MznRegression.from_args(self.args)

    @staticmethod
    def score_sum_to_sentiment(score):
        """
        The score_sum method returns a value < 0 for negative
        phrases and a value > 0 for positive phrases.
        >>> PhrasePredictor.score_sum_to_sentiment(None, -0.1)
        'neg'
        >>> PhrasePredictor.score_sum_to_sentiment(None, 0.0)
        'neu'
        >>> PhrasePredictor.score_sum_to_sentiment(None, 0.1)
        'pos'
        >>> PhrasePredictor.score_sum_to_sentiment(None, 9999)
        'pos'
        """
        if score == 0:
            return 'neu'
        elif score < 0:
            return 'neg'
        elif score > 0:
            return 'pos'
        else:
            raise ValueError("Invalid parameter: %s" % score)

    def score_sum(self, doc):
        doc_sum = 0.0
        for index in xrange(len(doc)):
            if doc[index] != 0.0:
                weight = self.coef_vector[index]
                doc_sum += weight
        return doc_sum

    @staticmethod
    def score_model_to_sentiment(score):
        """
        This method computes a sentiment value from the output
        of the movie review star rating regression model.
        A movie rating has been 0 and 5 stars.

        >>> PhrasePredictor.score_model_to_sentiment(None, 2.0)
        'neu'
        >>> PhrasePredictor.score_model_to_sentiment(None, 2.1)
        'neu'
        >>> PhrasePredictor.score_model_to_sentiment(None, 1.0)
        'neg'
        >>> PhrasePredictor.score_model_to_sentiment(None, 0.0)
        'neg'
        >>> PhrasePredictor.score_model_to_sentiment(None, 3.0)
        'neu'
        >>> PhrasePredictor.score_model_to_sentiment(None, 4.0)
        'neu'
        >>> PhrasePredictor.score_model_to_sentiment(None, '4.2')
        'pos'
        """
        if isinstance(score, basestring):
            score = float(score)
        if score >= 2 and score < 4:
            return "neu"
        elif score < 2:
            return "neg"
        elif score > 4:
            return "pos"
        else:
            raise ValueError("Invalid parameter: %s" % score)

    @staticmethod
    def sentiment_fine_grained_to_discrete_string(label):
        """
        This method maps a sentiment label between 0 and 4
        to the set of strings 'neg', 'neu' and 'pos'.
        @param label Sentiment label [0;4]
        @returns {string} 'neg', 'neu' or 'pos'
        >>>
        """
        v = PhrasePredictor.sentiment_fine_grained_to_discrete_value(
            label)
        ret = PhrasePredictor.sentiment_discrete_value_to_discrete_string(v)
        return ret

    @staticmethod
    def sentiment_fine_grained_to_discrete_value(label):
        """
        This method discretizes a sentiment label between
        0 and 4 in a space between 0 and 2.
        0 is negative,
        1 is neutral and
        2 is positive.

        Do not use this method to discretize the output of the
        regression model.
        """
        if isinstance(label, basestring):
            label = int(label)
        if isinstance(label, list):
            label = label[0]
        if label == 2:
            return 1
        elif label < 2:
            return 0
        elif label > 2:
            return 2
        else:
            raise ValueError("Unknown value: %s" % label)

    @staticmethod
    def sentiment_discrete_value_to_discrete_string(label):
        """
        This method returns a sentiment class label for a sentiment
        integer.
        This method can be used on the output of
        sentiment_fine_grained_to_discrete_value
        """
        if isinstance(label, basestring):
            label = int(label)
        if label == 0:
            return "neg"
        elif label == 1:
            return "neu"
        elif label == 2:
            return "pos"
        else:
            raise ValueError("Invalid parameter: %s" % label)

    def score_model(self, doc):
        if hasattr(self.model, "predict"):
            return self.model.predict([doc])
        else:
            return "N/A"

    @staticmethod
    def getSpan(tree):
        res = ""
        pos = tree.treepositions(order="preorder")
        for p in pos:
            if not hasattr(tree[p], "node"):
                res += " "
                res += tree[p]
        return res

    def evaluate(self, goldFile, csvFile=None):
        self.loadGoldTrees(goldFile)
        goldLabels = []
        rootGoldLabels = []
        spans = []
        predictedScoreSumLabels = []
        predictedModelLabels = []
        rootPredictedScoreSumLabels = []
        rootPredictedModelLabels = []
        for goldSentence in self.goldTrees:
            rGL = goldSentence.node
            span = self.getSpan(goldSentence)
            rGL = self.sentiment_fine_grained_to_discrete_string(rGL)
            (rScoreSum, rScoreModel) = self.main(span)
            rPredictedScoreSumSentiment = self.score_sum_to_sentiment(
                rScoreSum)
            rPredictedModelSentiment = self.score_model_to_sentiment(
                rScoreModel)
            rootPredictedScoreSumLabels.append(rPredictedScoreSumSentiment)
            rootPredictedModelLabels.append(rPredictedModelSentiment)
            rootGoldLabels.append(rGL)
            for goldNode in shared.ma_util.walkTree(goldSentence):
                goldSentiment = goldNode.node
                span = self.getSpan(goldNode)
                spans.append(span)
                (scoreSum, scoreModel) = self.main(span)
                goldSentiment = self.sentiment_fine_grained_to_discrete_string(
                    goldSentiment)
                goldLabels.append(goldSentiment)
                predictedScoreSumSentiment = self.score_sum_to_sentiment(
                    scoreSum)
                predictedModelSentiment = self.score_model_to_sentiment(
                    scoreModel)
                predictedScoreSumLabels.append(predictedScoreSumSentiment)
                predictedModelLabels.append(predictedModelSentiment)
        if self.dump_csv_file:
            assert len(spans) == len(predictedScoreSumLabels)
            assert len(spans) == len(predictedModelLabels)
            fh = open(self.dump_csv_file, 'w')
            writer = csv.writer(
                fh, delimiter="\t", quoting=csv.QUOTE_NONNUMERIC)
            for (span,
                 label1,
                 label2) in itertools.izip_longest(spans,
                                                   predictedScoreSumLabels,
                                                   predictedModelLabels):
                writer.writerow([span, label1, label2])
            fh.close()
        if csvFile:
            data = shared.evaluate.printStats(goldLabels,
                                              predictedScoreSumLabels,
                                              False)
            rootData = shared.evaluate.printStats(rootGoldLabels,
                                                  rootPredictedScoreSumLabels,
                                                  False, prefix="root")
            allNodes = shared.evaluate.ins(
                ['run', "type"], ['N/A', "ScoreSum"], data)
            allNodes.update(rootData)
            fh = open(csvFile, 'w')
            writer = csv.DictWriter(fh, allNodes.keys())
            writer.writeheader()
            writer.writerow(allNodes)
            # now do modelscore
            #data = projection.evaluate.printStats(goldLabels,
            #                                      predictedModelLabels,
            #                                      False)
            #rootData = projection.evaluate.printStats(rootGoldLabels,
            #                                         rootPredictedModelLabels,
            #                                          False, prefix="root")
#
#            allNodes = projection.evaluate.ins(
#                ['run', "type"], ['N/A', "ModelScore"], data)
#            allNodes.update(rootData)
#            writer.writerow(allNodes)
            fh.close()

    def main(self, phrase, returnCount=False):
        tokens = self.helper.split(phrase)
        doc = self.helper.convert_document_to_vector(tokens,
                                                     self.reverse_alphabet,
                                                     None)
        doc = doc.toarray()
        if len(doc) == 1:
            doc = doc[0]
        doc_score_sum = self.score_sum(doc)
        doc_score_model = self.score_model(doc)
        if returnCount:
            return (doc_score_sum, doc_score_model, len(doc))
        else:
            return (doc_score_sum, doc_score_model)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Score phrase against coefficient vector')
    parser.add_argument('--alphabet', required=True,
                        help='Alphabet pickle file')
    parser.add_argument('--model', required=True,
                        help='Predictor pickle file')
    parser.add_argument('--mzn-regression-args', required=True,
                        help='MznRegression argument pickle file')
    parser.add_argument('--phrase',
                        help='Phrase to score')
    parser.add_argument('--gold',
                        help='PTB file with gold annotations.')
    parser.add_argument('--dump-predictions',
                        help='Dump spans and sentiment prediction to TSV file')
    parser.add_argument('--csv-file', required='False',
                        help='Write evaluation data to CSV file.')
    args = parser.parse_args()
    logging.basicConfig(filename='evaluate_coef_sentiment_prediction.log',
                        level=logging.DEBUG,
                        format='%(asctime)s:%(module)s:'
                        + '%(levelname)s:%(message)s')
    logger.info("Starting. Config: %s", args)
    o = PhrasePredictor(args.alphabet, args.model, args.mzn_regression_args,
                        args.dump_predictions)
    if args.phrase:
        print o.main(args.phrase)
    if args.gold:
        o.evaluate(args.gold, args.csv_file)

#!/usr/bin/env python
# -*- coding: utf-8 -*-


from learn_mzn_review_score import MznRegression


# can't use cPickle, fails when loading large pickles.
# http://bugs.python.org/issue13555
#import cPickle as pickle
import pickle
import argparse
#from sklearn import svm
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error


class PhrasePredictor(object):
    def __init__(self, alphabet, model, args):
        self.alphabet_file = alphabet
        self.model_file = model
        self.args_file = args
        self.loadData()

    def loadData(self):
        self.alphabet = pickle.load(open(self.alphabet_file))
        self.model = pickle.load(open(self.model_file))
        self.args = pickle.load(open(self.args_file))
        self.reverse_alphabet = {}
        for token, index in self.alphabet.iteritems():
            self.reverse_alphabet[index] = token
        self.helper = MznRegression.from_args(self.args)
        self.helper.reverse_alphabet = self.reverse_alphabet

    def evaluate(self, goldFile):
        (goldDocs, goldLabels) = self.helper.build_test_vectors(goldFile)
        predicted = self.model.predict(goldDocs)
        mse = mean_squared_error(goldLabels, predicted)
        mae = mean_absolute_error(goldLabels, predicted)
        print "MSE: %.3f" % mse
        print "MAE: %.3f" % mae
        print "| %.3f | %.3f |" % (mse, mae)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Score phrase against coefficient vector')
    parser.add_argument('--alphabet', required=True,
                        help='Alphabet pickle file')
    parser.add_argument('--model', required=True,
                        help='Predictor pickle file')
    parser.add_argument('--mzn-regression-args', required=True,
                        help='MznRegression argument pickle file')
    parser.add_argument('--gold',
                        help='CSV file with FR reviews and scores.')
    args = parser.parse_args()
    o = PhrasePredictor(args.alphabet, args.model, args.mzn_regression_args)
    o.evaluate(args.gold)

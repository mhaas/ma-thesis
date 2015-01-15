#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script trains a regression learner which predicts the
review score (e.g. star rating) attached to a movie review.
"""

import nltk
import HTMLParser
import csv
import argparse
import os
import re
import hashlib
# cpickle is very, very broken :(
# http://bugs.python.org/issue10640
#import cPickle as pickle
import pickle
from sklearn import linear_model
from sklearn import svm
from sklearn.cross_validation import KFold
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import f1_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn import preprocessing
# for TF-IDF
from nltk.text import TextCollection, Text
from nltk.util import LazyConcatenation
from nltk.util import bigrams
import numpy as np
import scipy.sparse
np.set_printoptions(threshold=np.nan)
import logging
import itertools

logger = logging.getLogger("learn_mzn_review_score")


def gappy_bigrams(text):
    """
    >>> gappy_bigrams(["A", "B", "C"])
    [('A', 'C')]
    >>> gappy_bigrams(['A', 'B', 'C', 'D'])
    [('A', 'C'), ('B', 'D')]
    """
    bg = bigrams(text)
    last = None
    res = []
    for (w1, w2) in bg:
        if last is not None:
            gappy = (last[0], w2)
            res.append(gappy)
        last = (w1, w2)
    return res


class NotSoBrokenTextCollection(TextCollection):

    def __init__(self, source, name=None):
        if hasattr(source, 'words'):
            source = [source.words(f) for f in source.fileids()]
        self._texts = source
        Text.__init__(self, LazyConcatenation(source), name)
        self._idf_cache = {}


LARSCV = 'larscv'
LASSOCV = 'lassocv'
LLCV = 'lassolarscv'
LINSVR = 'linsvr'
RLASSO = 'randomizedlasso'
LINSVC = 'linsvc'
LINSVCSP = 'linsvcsparse'
AREG = 'ardregression'
ALL = 'ALL'


class MznRegression(object):

    @staticmethod
    def from_args(args):
        m = hashlib.md5()
        m.update(str(args))
        key = m.hexdigest()
        if hasattr(args, 'discretize'):
            discretize = args.discretize
        else:
            discretize = False
        o = MznRegression(args.use_frequency, args.use_tf_idf,
                          args.use_unigrams,
                          args.use_bigrams, args.scale_data,
                          args.use_gappy_bigrams, args.alphabet_size,
                          args.skip_singletons, args.learner, args.test_file,
                          args.skip_cv, discretize,
                          key)
        return o

    def __init__(self, useFrequencies, useTfIdf, useUnigrams,
                 useBigrams, scaleData, useGappyBigrams,
                 alphabetSize, skipSingletons, learners,
                 test, skipCV, discretize,
                 runKey):
        # TODO: smoothing for bigrams?
        self.useFrequencies = useFrequencies
        self.useTfIdf = useTfIdf
        self.tfIdf = None
        if self.useFrequencies and self.useTfIdf:
            raise ValueError("useFrequencies, useTfIdf is mutually exclusive")
        if not (useUnigrams or useBigrams or useGappyBigrams):
            raise ValueError("You must specify a set of features to include")
        self.useUnigrams = useUnigrams
        self.useBigrams = useBigrams
        self.scaleData = scaleData
        self.useGappyBigrams = useGappyBigrams
        self.alphabetSize = alphabetSize
        self.skipSingletons = skipSingletons
        self.learners = learners
        self.sentence_splitter = nltk.data.load('tokenizers/punkt/'
                                                + 'german.pickle')
        self.sentence_tokenizer = nltk.tokenize.TreebankWordTokenizer()
        self.test = test
        self.skipCV = skipCV
        self.discretize = discretize
        self.runKey = runKey

    def dump_object(self, obj, name):
        name = "%s_%s.pickle" % (name, self.runKey)
        fh = open(name, 'w')
        pickle.dump(obj, fh)
        fh.close()

    def clean(self, token):
        token = token.strip()
        token = token.lower()
        return token

    @staticmethod
    def split_rest(tokens):
        u"""NLTK tokenizer does not tokenize everything correctly.
        >>> MznRegression.split_rest(["ich.und", "hallo"])
        ['ich', 'und', 'hallo']
        >>> MznRegression.split_rest(["'ich.und", "hallo_", 'test!'])
        ['ich', 'und', 'hallo_', 'test']
        >>> MznRegression.split_rest([u"'ästhetischen"])
        [u'\\xe4sthetischen']
        >>> MznRegression.split_rest([u"'ästhetischen.keks"])
        [u'\\xe4sthetischen', u'keks']
        """
        res = []
        noise_re = re.compile(ur'[^\w\.]', re.UNICODE)
        regex = re.compile(ur'(\w+)\.(\w+)', re.UNICODE)
        for token in tokens:
            token = noise_re.sub("", token)
            m = regex.match(token)
            if m:
                res.append(m.group(1))
                res.append(m.group(2))
            else:
                res.append(token)
        return res
    @staticmethod
    def discretize_score(score):
        if score <= 2:
            return 0
        elif score >= 4:
            return 2
        else:
            return 1

    def split(self, document):
        """Tokenizes an entire document."""
        splitted = []
        for sentence in self.sentence_splitter.tokenize(document):
            for token in self.sentence_tokenizer.tokenize(sentence):
                cleaned = self.clean(token)
                if cleaned == "":
                    continue
                splitted.append(cleaned)
        splitted = self.split_rest(splitted)
        res = []
        if self.useUnigrams:
            res.extend(splitted)
        if self.useBigrams:
            res.extend(bigrams(splitted))
        if self.useGappyBigrams:
            res.extend(gappy_bigrams(splitted))
        return res

    def build_alphabet(self, documents):
        logger.info("Building alphabet")
        tfIdf = None
        if self.useTfIdf:
            logger.info("Building counts for TF-IDF")
            documentCollection = []
        res = {}
        #index = 0
        counts = {}
        for (document, label) in documents:
            if self.useTfIdf:
                currentDocument = []
                documentCollection.append(currentDocument)
            for token in self.split(document):
                logger.debug("Token: %s, Document: %s", token, document)
                if self.useTfIdf:
                    currentDocument.append(token)
                if token not in counts:
                    counts[token] = 0
                counts[token] += 1
        if self.useTfIdf:
            self.tfIdf = NotSoBrokenTextCollection(documentCollection,
                                                   name="TFIDF")
        logger.info("Got %s tokens" % len(counts))
        if self.skipSingletons:
            logger.info("Removing Hapax Legomena from alphabet")
            for (token, count) in counts.items():
                if count == 1:
                    logger.debug("Hapax legomenon: %s", token)
                    del counts[token]
            logger.info("Removed Hapax Legomena, now %s tokens", len(counts))
        else:
            logger.info("Not removing Hapax Legomena")
        # sorted tokens by frequency, retain most frequent K tokens
        truncated = sorted(counts.items(), key=lambda (token, count): count,
                           reverse=True)
        truncated = truncated[:self.alphabetSize]
        for index in xrange(len(truncated)):
            token = truncated[index][0]
            res[token] = index
        logger.info("Truncated to %s", len(res))
        logger.debug("alphabet is: %s", res)
        self.alphabet = res
        self.reverse_alphabet = {}
        for token, index in self.alphabet.iteritems():
            self.reverse_alphabet[index] = token
        return (res, tfIdf)

    def convert_document_to_vector(self, document, alphabet, tfIdf):
        res = []
        # faster lookup time
        if not (self.useTfIdf or self.useFrequencies):
            document = set(document)
        for x in xrange(len(alphabet)):
            token = alphabet[x]
            if self.useTfIdf:
                value = tfIdf.tf_idf(token, document)
            elif self.useFrequencies:
                value = document.count(token)
            else:
                if token in document:
                    value = 1
                else:
                    value = 0
            res.append(float(value))
        m = scipy.sparse.csr_matrix(res)
        return m

    def load_documents(self, csvFile):
        h = HTMLParser.HTMLParser()
        fh = open(csvFile)
        reader = csv.reader(fh)
        for row in reader:
            if len(row) < 8 or '<script' in row[8] or '<script' in row[3]:
                logger.debug("SKIPPING INVALID ROW")
                continue
            try:
                label = float(row[3])
            except ValueError:
                logger.debug("could not convert label, INVALID ROW")
                continue
            # 8 is the review title, 9 is the review text!
            if self.discretize:
                label = self.discretize_score(label)
            document = h.unescape(row[9].decode("utf-8"))
            yield (document, label)
        fh.close()

    def load_test_documents(self, csvFile, scale=5):
        fh = open(csvFile)
        reader = csv.reader(fh)
        for row in reader:
            label = float(row[0]) * scale
            if self.discretize:
                label = self.discretize_score(label)
            # 8 is the review title, 9 is the review text!
            document = row[1].decode("utf-8")
            yield (document, label)
        fh.close()

    def build_test_vectors(self, csvFile):
        source = self.load_test_documents(csvFile)
        return self._build_test_vectors(source)

    def _build_test_vectors(self, source):
        documents = None
        labels = []
        for (document, label) in source:
            bagOfWords = list(self.split(document))
            vec = self.convert_document_to_vector(bagOfWords,
                                                  self.reverse_alphabet,
                                                  self.tfIdf)
            logger.debug("Got document vector: %s", vec)
            if documents is None:
                documents = vec
            else:
                documents = scipy.sparse.vstack([documents, vec])
            labels.append(label)
        return (documents, labels)

    def build_vectors(self, csvFile):
        docSource = self.load_documents(csvFile)
        # k=None: include all terms...
        (alphabet, tfIdf) = self.build_alphabet(docSource)
        # re-initialize to reset iterator
        docSource = self.load_documents(csvFile)
        return self._build_test_vectors(docSource)

    def get_cv_folds(self, csvFile, n, folds=2):
        if self.skipCV:
            return None
        fileName = os.path.basename(csvFile)
        #fileName = csvFile
        m = hashlib.md5()
        m.update(fileName)
        key = m.hexdigest()
        fileName = "kfolds_%s.pickle" % key
        if os.path.exists(fileName):
            logger.info("Loading pickled folds")
            cv = pickle.load(open(fileName))
        else:
            cv = KFold(n, n_folds=folds, shuffle=True)
            pickle.dump(cv, open(fileName, 'w'))
            logger.info("Could not find pickled folds file.")
        assert cv.n == n
        assert cv.n_folds == folds
        return cv

    def build_classifier(self, csvFile):
        logger.info("Loading data from disk")
        (docs, labels) = self.build_vectors(csvFile)
        self.dump_object(self.alphabet, "alphabet")
        if self.test:
            t_d, t_l = self.build_test_vectors(self.test)
            self.test_data = t_d.toarray()
            self.test_labels = np.asarray(t_l)
        logger.info("Finished loading data")
        # need to convert or cross_val_score will throw
        print "Shape of Training data: %s" % (docs.shape,)
        if self.scaleData:
            docs = preprocessing.scale(docs)
        labels = np.asarray(labels)
        folds = self.get_cv_folds(csvFile, len(labels))
        logger.info("Converting sparse documents matrix to dense matrix.")
        dense_docs = docs.toarray()
        # great - none of the classifiers support a csr matrix.
        docs = dense_docs
        logger.info("Finished converting.")
        lassoLars = linear_model.LassoLarsCV()
        self.test_classifier(lassoLars, folds, dense_docs, labels, LLCV)
        # TODO: Set C to a value which will produce sparse coefficients
        linSVR = svm.SVR(kernel='linear')
        self.test_classifier(linSVR, folds, docs, labels, LINSVR)
        larsCV = linear_model.LarsCV()
        self.test_classifier(larsCV, folds, docs, labels, LARSCV)
        lassoCV = linear_model.LassoCV()
        self.test_classifier(lassoCV, folds, docs, labels, LASSOCV)
        randomLasso = linear_model.RandomizedLasso()
        # RandomizedLasso had advantages for data where features are highly
        # correlated.
        # TODO: what's a good alpha?
        # See
        # auto_examples/linear_model/plot_lasso_model_selection.html
        # Default is alpha='aic' ('Akaike information criterion (AIC)')
        self.test_classifier(randomLasso, folds, docs, labels,
                             RLASSO,
                             skipPredict=True)
        ardReg = linear_model.ARDRegression()
        self.test_classifier(ardReg, folds, docs, labels, AREG)
        print "TODO: try LinearSVC with class_weight='auto'"
        linsvc = svm.LinearSVC()
        self.test_classifier(linsvc, folds, docs, labels, LINSVC)
        linsvcsparse = svm.LinearSVC(penalty='l1', dual=False)
        self.test_classifier(linsvcsparse, folds, docs, labels, LINSVCSP)

    def extract_relevant_features(self, classifier):
        if not hasattr(classifier, 'coef_'):
            # for RandomizedLasso
            coeff_vector = classifier.scores_
        else:
            coeff_vector = classifier.coef_
        if len(coeff_vector) == 1:
            # some classifiers provide one vector per class
            # even for regression
            coeff_vector = coeff_vector[0]
        vectors = []
        # handle multi-class case, != regression
        if not self.discretize:
            vectors.append(coeff_vector)
        else:
            vectors = coeff_vector
        counts = []
        for classIndex in xrange(len(vectors)):
            coeff_vector = vectors[classIndex]
            count = 0
            for index in xrange(len(coeff_vector)):
                coef = coeff_vector[index]
                if coef != 0:
                    logger.info("Class %s Coef %s (%s): %s",
                                classIndex,
                                index,
                                self.reverse_alphabet[index],
                                coef)
                    count += 1
            logger.info("Extracted %s features for class %s", count,
                        classIndex)
            counts.append(count)
        return counts

    def test_classifier_on_test_set(self, classifier, train_data, train_labels,
                                    test_data, test_labels, name,
                                    skipPredict=False):
        if skipPredict:
            logger.info("Skipping test on test set for %s", name)
            print "%s SKIPPED" % name
            return
        print name
        classifier.fit(train_data, train_labels)
        self.dump_object(classifier, name)
        predicted = classifier.predict(test_data)
        self.print_eval([test_labels], [predicted], classifier)

    def test_classifier_cv(self, classifier, folds, data, labels,
                           name, skipPredict=False):
        print name
        logger.info("Testing %s", name)
        logger.info("Training classifier on FULL data set to select features")
        classifier.fit(data, labels)
        logger.info("Finished training")
        self.dump_object(classifier, name)
        count = self.extract_relevant_features(classifier)
        print "Extracted %s features on full data set." % count
        if skipPredict or self.skipCV:
            logger.info("Skipping CV test for %s", name)
            print "%s SKIPPED" % name
            return
        golds = []
        predicteds = []
        for train_index, test_index in folds:
            logger.debug("Current Fold: train_index %s, test_index %s",
                         train_index,
                         test_index)
            train_data = data[train_index]
            train_label = labels[train_index]
            test_data = data[test_index]
            test_labels = labels[test_index]
            logger.info("Train size: %s, Test size: %s",
                        len(train_data),
                        len(test_data))
            classifier.fit(train_data, train_label)
            predicted = classifier.predict(test_data)
            golds.append(test_labels)
            predicteds.append(predicted)
        self.print_eval(golds, predicteds, classifier)

    def test_classifier(self, classifier, folds, data, labels,
                        name, skipPredict=False):
        if not (name in self.learners or ALL in self.learners):
            logger.info("Skipping %s", name)
            print "%s SKIPPED" % name
            return
        if self.test:
            logger.info("Testing on test set!")
            self.test_classifier_on_test_set(classifier, data, labels,
                                             self.test_data, self.test_labels,
                                             name, skipPredict)
        else:
            logger.info("Testing using CV!")
            self.test_classifier_cv(classifier, folds, data, labels,
                                    name, skipPredict)

    def print_eval(self, gold, predicted, classifier):
        if self.discretize:
            self.print_eval_discretized_folds(gold, predicted, classifier)
        else:
            self.print_eval_reg_folds(gold, predicted, classifier)

    def print_eval_reg_folds(self, gold, predicted, classifier):
        mses = []
        maes = []
        counts = []
        for (goldFold, predictedFold) in itertools.izip(gold, predicted):
            (mse, mae, count) = self.print_eval_reg(goldFold, predictedFold,
                                                    classifier)
            mses.append(mse)
            maes.append(mae)
            counts.append(count)
        counts = np.array(counts)
        mses = np.array(mses)
        maes = np.array(maes)
        msg1 = "MSE         MAE         FEATURES"
        msg2 = "%.3f (%.3f) %.3f (%.3f) %.3f (%.3f)" % (mses.mean(),
                                                        mses.std(),
                                                        maes.mean(),
                                                        maes.std(),
                                                        counts.mean(),
                                                        counts.std())
        print msg1
        print msg2
        logger.info(msg1)
        logger.info(msg2)

    def print_eval_reg(self, gold, predicted, classifier):
        mse = mean_squared_error(gold, predicted)
        mae = mean_absolute_error(gold, predicted)
        logger.info("Extracting features for current fold")
        count = self.extract_relevant_features(classifier)
        logger.info("MSE: %s", mse)
        logger.info("MAE: %s", mae)
        logger.info("Count: %s", count)
        return (mse, mae, count)

    def print_eval_discretized(self, gold, predicted, classifier):
        print gold
        print predicted
        f1 = f1_score(gold, predicted, average=None)
        rep = classification_report(gold, predicted,
                                    labels=[0, 1, 2],
                                    target_names=['neg', 'neu', 'pos'])
        cm = confusion_matrix(gold, predicted)
        count = self.extract_relevant_features(classifier)
        macrof1 = f1_score(gold, predicted, average="macro")
        print "F1 scores for fold: %s" % f1
        print "Classification report for fold: %s" % rep
        print "Confusion matrix: %s" % cm
        print "Count: %s" % count
        logger.info(rep)
        return macrof1

    def print_eval_discretized_folds(self, gold, predicted, classifier):
        macrof1s = []
        for (goldFold, predictedFold) in itertools.izip(gold, predicted):
            macrof1 = self.print_eval_discretized(goldFold, predictedFold,
                                                  classifier)
            macrof1s.append(macrof1)
        macrof1s = np.asarray(macrof1s)
        print "Overall Macro F1: %.3f (%.3f)" % (macrof1s.mean(),
                                                 macrof1s.std())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Learn regression of MZN movie'
        + ' reviews against their score.')
    parser.add_argument('--input', required=True,
                        help='Input CSV File')
    parser.add_argument('--use-frequency', action="store_true",
                        help='Use term frequency instead of binary features.')
    parser.add_argument('--use-tf-idf', action="store_true",
                        help='Use TF-IDF score instead of binary features.')
    parser.add_argument('--use-unigrams', action='store_true',
                        help='Use Unigrams.')
    parser.add_argument('--use-bigrams', action='store_true',
                        help='Use Bigrams.')
    parser.add_argument('--use-gappy-bigrams', action='store_true',
                        help='Add gappy bigrams to other features')
    parser.add_argument('--scale-data', action='store_true',
                        help='Standardize data (Gaussian with zero mean'
                        + ' and unit variance).')
    parser.add_argument('--alphabet-size', type=int,
                        help='Keep ALPHABET_SIZE most frequent tokens')
    parser.add_argument('--skip-singletons', action='store_true',
                        help='Remove hapax legomena from alphabet.')
    parser.add_argument('--learner', action='append',
                        required=True,
                        choices=[LARSCV, LASSOCV, LLCV, LINSVR,
                                 RLASSO, AREG, ALL, LINSVC, LINSVCSP],
                        help='Specify which learners to use')
    parser.add_argument('--test-file',
                        help='If used, will test on TESTFILE instead of'
                        + ' cross-validation.')
    parser.add_argument('--skip-cv', action='store_true',
                        help='Skip CV and just create model.')
    parser.add_argument('--discretize', action='store_true',
                        help='Discretize five-star ratings into {pos, neg, neutral}')
    args = parser.parse_args()
    m = hashlib.md5()
    m.update(str(args))
    key = m.hexdigest()
    print "%s: %s" % (key, str(args))
    logger_filename = "learn_mzn_review_score-%s.log" % key
    print "Logging go %s" % logger_filename
    logging.basicConfig(filename=logger_filename, level=logging.INFO,
                        format='%(asctime)s:%(module)s:'
                        + '%(levelname)s:%(message)s')
    logger.info("Starting. Config: %s", args)
    o = MznRegression.from_args(args)
    o.build_classifier(args.input)
    outFH = open("args_%s.pickle" % key, "w")
    pickle.dump(args, outFH)
    outFH.close()

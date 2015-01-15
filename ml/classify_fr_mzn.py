#!/usr/bin/python
# -*- coding: utf-8 -*-
"""This script loads representations of FR and MZN documents
and builds several classifiers. Evaluation metrics are printed
to stdout."""

import sys
import csv
import numpy as np
from sklearn import svm
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.cross_validation import train_test_split
from sklearn.feature_selection import RFECV
from sklearn.feature_selection import chi2
from sklearn.ensemble import AdaBoostClassifier


def read_topic_file(fileName):
    # returned list is zero-based
    res = []
    # use with topic-keys file
    fh = open(fileName)
    for line in fh.readlines():
        tokens = line.split(" ")
        res.append(tokens[2:])
    return res


def print_topic_keys(topicList, topicKeys):
    if isinstance(topicList[0], tuple):
        topicList = map(lambda (topic, rank): topic, topicList)
    for index in topicList:
        print topicKeys[index]


def get_best_features(ranking, x):
    res = []
    for index in xrange(len(ranking)):
        res.append((index, ranking[index]))
    return sorted(res, key=lambda (index, val): val)[-x:]


def read_csv_from_file(fileName):
    fh = open(fileName)
    res = read_csv(fh)
    fh.close()
    return res


def read_csv(fh):
    res = []
    for row in csv.reader(fh):
        del row[0]
        del row[0]
        numbers = map(lambda x: float(x), row)
        res.append(numbers)
    return res


def classify(classifier, trainData, testData, trainLabel, testLabel, topicKeys,
             skipRFE):
    classifier.fit(trainData, trainLabel)
    predicted = classifier.predict(testData)
    print "== Confusion Matrix =="
    print confusion_matrix(testLabel, predicted)
    print "(Row: Gold, Column: Predicted)"
    print classification_report(testLabel, predicted)
    (stats, pval) = chi2(trainData, trainLabel)
    print "== Best Features (chi^2) =="
    best_features = get_best_features(stats, 10)
    print best_features
    print_topic_keys(best_features, topicKeys)
    if not skipRFE:
        print "== Best Features (RFE) =="
        rfecv = RFECV(classifier)
        rfecv.fit(trainData, trainLabel)
        best_features = get_best_features(rfecv.ranking_, 10)
        print best_features
        print_topic_keys(best_features, topicKeys)


def main(frFile, mznFile, topicKeysFile):
    topicKeys = read_topic_file(topicKeysFile)
    fr = read_csv_from_file(frFile)
    mzn = read_csv_from_file(mznFile)
    labels = np.concatenate([[0 for x in range(0, len(fr))],
                             [1 for x in range(0, len(mzn))]])
    fr_mzn = np.concatenate([fr, mzn])
    (fr_mzn_data_train,
     fr_mzn_data_test,
     fr_mzn_labels_train,
     fr_mzn_labels_test) = train_test_split(fr_mzn, labels, test_size=0.8)
    classifiers = {"ada": AdaBoostClassifier(),
                   "svc": svm.SVC(),
                   "linsvc": svm.SVC(kernel="linear")}
    for (name, classifier) in classifiers.iteritems():
        print "Invoking classifier: %s" % name
        if name != "linsvc":
            skipRFE = True
        else:
            skipRFE = False
        classify(classifier,
                 fr_mzn_data_train,
                 fr_mzn_data_test,
                 fr_mzn_labels_train,
                 fr_mzn_labels_test,
                 topicKeys,
                 skipRFE)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])

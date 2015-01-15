
#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
from sklearn import svm
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
#from sklearn.cross_validation import cross_val_score
import numpy as np
from classify_fr_mzn import read_csv
import argparse
#from scipy.stats import spearmanr


def makeLabels(data0, data1):
    labels = np.concatenate([[0 for x in range(0, len(data0))],
                             [1 for x in range(0, len(data1))]])
    return labels


def makeClassifier():
    classifier = svm.SVC(kernel="linear", class_weight="auto",
                         probability=True)
    return classifier


def printEval(classifier, test_data, test_labels):
    predicted = classifier.predict(test_data)
    print classification_report(test_labels, predicted)
    print confusion_matrix(test_labels, predicted)


def getBestByProbability(classifier, to_classify):
    probabilities = classifier.predict_proba(to_classify)
    #desired_class = 0
    #desired_class_index = classifier.classes_.find(desired_class)
    best_class0 = []
    best_class1 = []
    for index in xrange(len(probabilities)):
        cur_prob = probabilities[index]
        if cur_prob[0] > cur_prob[1]:
            target = best_class0
            prob = cur_prob[0]
        else:
            target = best_class1
            prob = cur_prob[1]
        target.append((index, prob))
    best_class0 = sorted(best_class0, key=lambda (index, prob): prob)
    #print best_class0[:100]
    return best_class0


def getBest(classifier, to_classify):
    distances = classifier.decision_function(to_classify)
    #predicted = classifier.predict(to_classify)
    # distances contains only one distance because we only have one
    # hyperplane - two classes.
    # TODO: or do we want to use predict_proba?
    best_pos = []
    best_neg = []
    for index in xrange(len(distances)):
        #pred_class = predicted[index]
        val = distances[index][0]
        #print "value is %s, pred_class is %s" % (pred_class, val)
        if val <= 0:
            target = best_neg
        else:
            target = best_pos
        target.append((index, val))
    best_pos = sorted(best_pos, key=lambda (index, dist): dist, reverse=True)
    best_neg = sorted(best_neg, key=lambda (index, dist): dist)
    #print best_pos[0:100]
    # < 0 is class 0, which is 'useful' reviews
    print "Class 0 has %s items, Class 1 has %s items" % (len(best_neg),
                                                          len(best_pos))
    print best_neg[0:100]
    return (best_neg, best_pos)


def to_csv(data, fileName):
    fh = open(fileName, 'w')
    writer = csv.writer(fh)
    for (index, score) in data:
        writer.writerow((index, score))
    fh.close()


def main(train0, train1, test0, test1, to_classify, outFileZero, outFileOne):
    train0_data = read_csv(train0)
    train1_data = read_csv(train1)
    train_data = np.concatenate([train0_data, train1_data])
    train_labels = makeLabels(train0_data, train1_data)
    test0_data = read_csv(test0)
    test1_data = read_csv(test1)
    test_data = np.concatenate([test0_data, test1_data])
    test_labels = makeLabels(test0_data, test1_data)
    classifier = makeClassifier()
    classifier.fit(train_data, train_labels)
    print "Evaluation results on test data:"
    printEval(classifier, test_data, test_labels)
    to_classify_data = read_csv(to_classify)
    (bestZero, bestOne) = getBest(classifier, to_classify_data)
    #best_by_prob = getBestByProbability(classifier, to_classify_data)
    # SVC uses one-vs-one scheme
    # As opposed to one-vs-rest
    #best_i = map(lambda (index, prob): index, bestZero)
    #best_by_prob_i = map(lambda (index, prob): index, best_by_prob)
    print "len bestZero %s, len bestOne %s" % (len(bestZero), len(bestOne))
    # won't work: best_by_prob varies wildly, dimensions don't match
    #rank_corr = spearmanr(best_i, best_by_prob_i)
    #print "Spearman rank corr between best and best_by_prob: %s" % rank_corr
    to_csv(bestZero, outFileZero)
    if outFileOne:
        to_csv(bestOne, outFileOne)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Get "useful" MZN reviews'
        + ' with highested prediction confidence score')
    parser.add_argument('--train0', required=True, type=file,
                        help='Input CSV File - Train Data - Class 0')
    parser.add_argument('--train1', required=True, type=file,
                        help='Input CSV File - Train Data - Class 1')
    parser.add_argument('--test0', required=True, type=file,
                        help='Input CSV File - Test Data - Class 0')
    parser.add_argument('--test1', required=True, type=file,
                        help='Input CSV File - Test Data - Class 1')
    parser.add_argument('--to-classify', required=True, type=file,
                        help='Input CSV File - Data to classify')
    parser.add_argument('--out-zero', required=True,
                        help='Output CSV File for Class 0 - Zero-based'
                        + ' indices and scores')
    parser.add_argument('--out-one',
                        help='Output CSV File for Class 1 - Zero-based'
                        + ' indices and scores')
    args = parser.parse_args()
    main(args.train0, args.train1, args.test0, args.test1, args.to_classify,
         args.out_zero, args.out_one)

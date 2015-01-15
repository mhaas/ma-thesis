#!/usr/bin/env python
# -*- coding: utf-8 -*-
import itertools
import math
import csv
import sys
from collections import OrderedDict
import ma_util
import ml.feature_extraction


"""
This module holds several functions related to the evaluation
of classifiers.
"""


def getCoarseGrainedTreeLabelsFile(fileName):
    return getCoarseGrainedTreeLabels(ma_util.readPenn(fileName))


def getCoarseGrainedTreeLabels(trees):
    """Extracts root and node labels from collection of trees.

    The trees are assumed to have fine-grained labels. The resulting
    label lists are collapsed into the coarse-grained space.

    This method returns a tuple of rootLabel and nodeLabel lists.

    @param trees {Iterable<nltk.Tree.tree>} Collection of trees
    @returns {Tuple<list,list>} Root and node labels
    """
    return getTreeLabels(trees, ma_util.GRANULARITY_COARSE)


def getTreeLabelsFile(fileName, granularity):
    return getTreeLabels(ma_util.readPenn(fileName), granularity)


def getTreeLabels(trees, granularity):
    """Extracts root and node labels from collection of trees.

    The trees are assumed to have fine-grained labels. The resulting
    label lists are collapsed into the granularity space defined
    by the granularity parameter.

    This method returns a tuple of rootLabel and nodeLabel lists.

    @param trees {Iterable<nltk.Tree.tree>} Collection of trees
    @param granularity {str} Granularity level
    @returns {Tuple<list,list>} Root and node labels
    """
    rootLabels = []
    nodeLabels = []
    # TODO: used to ignore granularity here - what was affected?
    extractor = ml.feature_extraction.GoldExtractor(granularity=granularity)
    for tree in trees:
        treeLabels = extractor.extract_gold_sentiment(tree)
        # the first node is the root node, thus holds sentiment
        # for the full sentence
        rootLabels.append(treeLabels[0])
        nodeLabels.extend(treeLabels)
    return (rootLabels, nodeLabels)


def getTreeLabelsAtLengthFile(fileName, granularity):
    return getTreeLabelsAtLength(ma_util.readPenn(fileName), granularity)


def getTreeLabelsAtLength(trees, granularity):
    res = {}
    extractor = ml.feature_extraction.GoldExtractor(granularity=granularity)
    for tree in trees:
        treeLabels = extractor.extract_gold_sentiment(tree, extractLength=True)
        for (label, length) in treeLabels:
            if length not in res:
                res[length] = []
            res[length].append(label)
    return res


def countMarginals(goldLabels, predictedLabels, desiredClass):
    """
    Given a list of gold labels and predicted labels,
    returns the marginals of the confusion matrix.

    The iterables passed in can be any data type, but they should
    be comparable. The desiredClass parameter should be the same data
    type.

    @param goldLabels {Iterable} Gold labels
    @param predictedLabels {Iterable} predicted labels
    @param desiredClass {anything} Class of the interest
    """
    truePositive = 0.0
    falsePositive = 0.0
    trueNegative = 0.0
    falseNegative = 0.0
    assert len(goldLabels) == len(predictedLabels)
    for (gL, pL) in itertools.izip_longest(goldLabels,
                                           predictedLabels,
                                           fillvalue=
                                           "LIST_LENGTH_NOT_EQUAL"):
        if (gL == desiredClass and pL == desiredClass):
            truePositive += 1
        elif (gL == desiredClass and pL != desiredClass):
            falseNegative += 1
        elif (gL != desiredClass and pL == desiredClass):
            falsePositive += 1
        elif (gL != desiredClass and pL != desiredClass):
            trueNegative += 1
        else:
            raise ValueError("Should not have gotten here.")
    return (truePositive, falsePositive, trueNegative, falseNegative)


def moreStats(goldLabels, predictedLabels, desiredClass):
    """
    Computes several statistics given gold and predicted labels.

    Returns a four-tuple containing precision, recall, F1 and
    accuracy.

    This method can return NaN in some cases.

    @param goldLabels {Iterable} Gold labels
    @param predictedLabels {Iterable} predicted labels
    @param desiredClass {anything} Class of the interest
    @returns {tuple<float,float,float,float>} Statistics
    """
    (truePositive, falsePositive,
     trueNegative, falseNegative) = countMarginals(goldLabels,
                                                   predictedLabels,
                                                   desiredClass)
    assert len(goldLabels) == (truePositive + trueNegative
                               + falsePositive + falseNegative)
    if (truePositive + falsePositive == 0):
        precision = float("NaN")
    else:
        precision = (truePositive) / (truePositive + falsePositive)
    if (truePositive + falseNegative == 0):
        recall = float("NaN")
    else:
        recall = (truePositive) / (truePositive + falseNegative)
    if ((precision == 0 and recall == 0)
            or math.isnan(precision) or math.isnan(recall)):
        fmeasure = float("NaN")
    else:
        fmeasure = 2 * ((precision * recall) / (precision + recall))
    acc = (truePositive + trueNegative) / (truePositive + trueNegative
                                           + falsePositive
                                           + falseNegative)
    return (precision, recall, fmeasure, acc)


def printStatsCoarseInt(goldLabels, predictedLabels,
                        prefix=None):
    """
    Generate statistics for coarse-grained setting where each label
    is represented as an integer:
        negative: 0
        neutral: 1
        positive: 2

    The returned statistics will be contained in a collections.OrderedDict
    instance. The mapping is from {string} keys to {float} or {int}.

    @param goldLabels {Iterable} Gold labels
    @param predictedLabels {Iterable} predicted labels
    @param desiredClass {object} Class of the interest
    @param prefix {string} Prefix (rather, Infix) to mark keys
    @returns {OrderedDict} Statistics
    """
    return printStats(goldLabels, predictedLabels, False, prefix=prefix,
                      negLabel=ma_util.NEG, neuLabel=ma_util.NEU,
                      posLabel=ma_util.POS)


def printStatsSubj(goldLabels, predictedLabels, subjLabel,
                   objLabel):
    """
    Gather statistics for subjective/objective classification.
    There is no distinction between root labels and node labels.

    The returned statistics will be contained in a collections.OrderedDict
    instance. The mapping is from {string} keys to {float} or {int}.

    @param goldLabels {Iterable} Gold labels
    @param predictedLabels {Iterable} predicted labels
    @param subjLabel {object} Label for subjective class
    @param objLabel {object} Label for objective class
    """
    data = OrderedDict()
    for (desiredClazz, desiredClazzLabel) in [(objLabel, 'Objective'),
                                              (subjLabel, 'Subjective')]:
        _statsPerClass(data, goldLabels, predictedLabels, desiredClazz,
                       desiredClazzLabel)
    data[_accMacroKey()] /= 2.0
    data[_fMacroKey()] /= 2.0
    return data


def _statsPerClass(data, goldLabels, predictedLabels, desiredClazz,
                   desiredClazzLabel, infix="", combinedInfix=""):
    """
    Generate statistics per class.

    Macro accuracy and macro F1 are summed here and must be divided by
    the number of classes by the caller.
    """
    (precision, recall,
     fmeasure, accuracy) = moreStats(goldLabels,
                                     predictedLabels,
                                     desiredClazz)
    data[desiredClazzLabel + infix + 'FScore'] = fmeasure
    data[desiredClazzLabel + infix + 'Acc'] = accuracy
    if _accMacroKey(combinedInfix) not in data:
        data[_accMacroKey(combinedInfix)] = 0
    if _fMacroKey(combinedInfix) not in data:
        data[_fMacroKey(combinedInfix)] = 0
    data[_accMacroKey(combinedInfix)] += accuracy
    data[_fMacroKey(combinedInfix)] += fmeasure


def _accMacroKey(combinedInfix=''):
    """
    Returns key for macro accuracy.
    """
    return 'combined' + combinedInfix + 'AccMacro'


def _fMacroKey(combinedInfix=''):
    """
    Returns key for macro F1.
    """
    return 'combined' + combinedInfix + 'FMacro'


def printStats(goldLabels, predictedLabels, showPercentages,
               prefix=None, negLabel="neg", neuLabel="neu",
               posLabel="pos"):
    # TODO: more documentation
    """
    Calculates classification statistics based on a list of
    gold labels and predicted labels.
    """
    if prefix is None:
        prefix = ""
    # prefix actually becomes an infix
    # if prefix is not none, then we capitalize the following L in 'label'
    if len(prefix) != 0:
        infix = prefix + 'Label'
        combinedInfix = prefix.capitalize() + 'Label'
    else:
        infix = 'label'
        combinedInfix = 'Label'
    data = OrderedDict()
    data[infix + 'sAcc'] = '-1'
    # normally, we assume we get fine-grained labels OR coarse-grained labels
    # in string form - and it's been that way for a while
    # so as not to break API, we only mangle the labels if the defaults are
    # not integer
    if not ((isinstance(negLabel, int) or
            isinstance(neuLabel, int) or isinstance(posLabel, int))):
        goldLabels = mapNumericsToSentiment(goldLabels)
        predictedLabels = mapNumericsToSentiment(predictedLabels)
    for (desiredClazz, desiredClazzLabel) in [(negLabel, 'Negative'),
                                              (neuLabel, 'Neutral'),
                                              (posLabel, 'Positive')]:
        _statsPerClass(data, goldLabels, predictedLabels, desiredClazz,
                       desiredClazzLabel,
                       infix, combinedInfix)
    data[_accMacroKey(combinedInfix)] /= 3.0
    data[_fMacroKey(combinedInfix)] /= 3.0
    return data


def statsToFile(data, fileName, multi=False, delim=','):
    if hasattr(fileName, 'write'):
        fh = fileName
    else:
        fh = open(fileName, 'w')
    if multi:
        if not len(data) > 0:
            raise ValueError("Need at least one row to write.")
        keys = data[0].keys()
    else:
        keys = data.keys()
    writer = csv.DictWriter(fh, keys, delimiter=delim)
    writer.writeheader()
    if multi:
        writer.writerows(data)
    else:
        writer.writerow(data)
    if fh != sys.stdout and fh != sys.stderr:
        fh.close()


def ins(items, keys, od):
    n = OrderedDict()
    for (key, val) in itertools.izip_longest(items, keys):
        n[key] = val
    for (key, val) in od.iteritems():
        n[key] = val
    return n


def mapNumericsToSentiment(nodeLabels):
    res = []
    for label in nodeLabels:
        label = str(label)
        if label in ["neg", "neu", "pos"]:
            res.append(label)
        elif label == "0" or label == "1":
            res.append("neg")
        elif label == "2":
            res.append("neu")
        elif label == "3" or label == "4":
            res.append("pos")
        else:
            raise ValueError("Unknown sentiment label: %s" % label)
    return res

from sklearn.metrics import accuracy_score


def accuracyAtNAllNeutral(goldFile, granularity):
    gold = getTreeLabelsAtLengthFile(goldFile, granularity)
    res = {}
    for key in sorted(gold.keys()):
        if granularity == ma_util.GRANULARITY_COARSE:
            allNeu = [ma_util.NEU for x in gold[key]]
        elif granularity == ma_util.GRANULARITY_FINE:
            allNeu = [ma_util.FINE_NEU for x in gold[key]]
        else:
            raise ValueError("Unknown granularity: %s" % granularity)
        score = accuracy_score(gold[key], allNeu)
        res[key] = (score, len(gold[key]))
    return res


def accuracyAtN(goldFile, predFile, granularity):
    gold = getTreeLabelsAtLengthFile(goldFile, granularity)
    pred = getTreeLabelsAtLengthFile(predFile, granularity)
    res = {}
    assert gold.keys() == pred.keys()
    for key in sorted(gold.keys()):
        score = accuracy_score(gold[key], pred[key])
        res[key] = (score, len(gold[key]))
    return res

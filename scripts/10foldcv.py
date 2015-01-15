#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script splits a input file by lines into 10 different splits
# and produces 10 different folds
# Each fold is divided in 2 parts DEV, 1 part TEST and 7 parts TRAIN

import os
import sys
import numpy
import shutil
import tigerhelper as th
from lxml import etree

import argparse

FOLDS = 10


def wrapAt(someList, numFolds):
    res = []
    for item in someList:
        if item >= numFolds:
            res.append(item - numFolds)
        else:
            res.append(item)
    return res


def get_indices_thesis(numFolds):
    """
    Produces duplicate items across the train sets.
    Only useful for legacy purposes.
    """
    res = []
    for x in xrange(numFolds):
        dev = wrapAt([x], numFolds)
        test = wrapAt([x + 1], numFolds)
        # leaves one slice out
        # before, the missing slice (x+2) would end up in test
        # as this generates duplicates in the test set across splits,
        # this is obviously not useful
        train = wrapAt(range(x + 3, x + numFolds), numFolds)
        res.append((train, test, dev))
    return res


def get_indices(numFolds):
    res = []
    for x in xrange(numFolds):
        dev = wrapAt([x], numFolds)
        test = wrapAt([x + 1], numFolds)
        # crucial: the following leaves one slice out
        train = wrapAt(range(x + 2, x + numFolds), numFolds)
        res.append((train, test, dev))
    return res


def get_folds(someList, numFolds):
    folds = numpy.array_split(someList, numFolds)
    return folds


def read_text_items(fileName):
    fh = open(fileName, 'r')
    lines = fh.readlines()
    fh.close()
    return lines


def read_tiger_items(fileName):
    helper = th.TigerHelper(fileName)
    res = []
    for item in th.getSentences(helper.tree):
        # have to serialize these, or numpy.array_split
        # will return weird splits. It looks like it uses the individual
        # sentence nodes as iterables.
        res.append(etree.tostring(item))
    return res


def write_set(someSet, outDir, name):
    fh = open(os.path.join(outDir, name), 'w')
    for fold in someSet:
        for line in fold:
            fh.write(str(line))
    fh.close()


def write_tiger_set(someSet, outDir, name):
    res = []
    for fold in someSet:
        for sentence in fold:
            # print sentence
            elem = etree.fromstring(sentence)
            # print elem
            res.append(elem)
    tree = th.constructTigerXML(res)
    fh = open(os.path.join(outDir, name), 'w')
    fh.write(etree.tostring(tree, encoding='UTF-8'))
    fh.close()


def all_disjunct(trainI, testI, devI):
    assert set(trainI).isdisjoint(set(testI))
    assert set(trainI).isdisjoint(set(devI))
    assert set(devI).isdisjoint(set(testI))


def sub_list(someList, indices):
    res = []
    for index in indices:
        res.append(someList[index])
    return res


def main(fileName, outDir, thesisMode):
    if fileName.endswith('.xml'):
        isXML = True
        lines = read_tiger_items(fileName)
    else:
        isXML = False
        lines = read_text_items(fileName)
    slices = numpy.asarray(get_folds(lines, FOLDS))
    if thesisMode:
        indices = get_indices_thesis(FOLDS)
    else:
        indices = get_indices(FOLDS)
    count = 0
    for (trainI, testI, devI) in indices:
        all_disjunct(trainI, testI, devI)
        print >> sys.stderr, (("Split %s with folds train: %s, test: %s,"
                              + " dev: %s") %
                              (count, trainI, testI, devI))
        foldDir = os.path.join(outDir, "fold_%s" % count)
        if os.path.exists(foldDir):
            shutil.rmtree(foldDir)
        os.makedirs(foldDir)
        train = slices[trainI]
        test = slices[testI]
        dev = slices[devI]
        # fun stuff: the following apparently overrides write_set
        # from the global name space due to some global-ness issues
        # if isXML:
        #    write_set = write_tiger_set
        if isXML:
            cur_write_set = write_tiger_set
        else:
            cur_write_set = write_set
        cur_write_set(train, foldDir, "train")
        cur_write_set(test, foldDir, "test")
        cur_write_set(dev, foldDir, "dev")
        count += 1

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Generate splits for 10fold CV.')
    parser.add_argument('--input', required=True,
                        help='File containing data. PTB or TigerXML.')
    parser.add_argument('--output', required=True,
                        help='Output directory where folds are stored')
    # The setting is here for reproducibility
    parser.add_argument('--thesis-mode', required=False,
                        action='store_true',
                        help='Leaves out one slice in train set. Not useful.')
    args = parser.parse_args()
    main(args.input, args.output, args.thesis_mode)

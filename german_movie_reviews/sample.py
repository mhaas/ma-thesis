#!/usr/bin/python
# -*- coding: utf-8 -*-

import glob
import random
import os
import sys
import re
import tigerhelper
from lxml import etree


def normalize(sentence):
    u"""Removes any non-alphanumeric character from a string.

    >>> normalize('foo9!')
    'foo9'
    >>> normalize('"Hallo_ Welt.12"')
    'hallo_welt12'
    """
    return re.sub("\W", "", sentence).lower()


def lookup(sentence, sentences):
    normalized = normalize(sentence)
    for (key, value) in sentences.iteritems():
        if value == normalized:
            return key
    return None


def writeSamples(sentences, filePrefix, count, tigerFile):
    tigerSentences = tigerhelper.readTreebankMap(tigerFile, normalize)
    tigerXML = tigerhelper.TigerHelper(tigerFile)

    fhM = open(filePrefix + ".meta", "w")
    fh = open(filePrefix + ".txt", "w")
    validSamples = 0
    sampledTiger = []
    while validSamples < count:
        s = random.choice(sentences)
        print s
        sentenceID = lookup(s[2], tigerSentences)
        if not sentenceID:
            print "Could not look up sentence %s" % (s,)
            continue
        else:
            validSamples += 1
            sampledTiger.append(tigerXML.getSentence(sentenceID))
        fhM.write(str(sentenceID))
        fhM.write("\n")
        fh.write(s[2].strip())
        fh.write("\n")
    fh.close()
    fhM.close()
    newTiger = tigerhelper.constructTigerXML(sampledTiger)
    etree.ElementTree(newTiger).write(filePrefix + ".xml")


def sample(directory, tigerFile):
    print "running"
    lowerHalf = []
    upperHalf = []
    for fileName in glob.iglob(os.path.join(directory, "*.html.txt.split")):
        fh = open(fileName, "r")
        sentences = []
        for sentence in fh.readlines():
            sentences.append(sentence)
        for index in xrange(len(sentences)):
            if index < len(sentences) / 2:
                target = upperHalf
            else:
                target = lowerHalf
            target.append((os.path.basename(fileName),
                           index,
                           sentences[index]))
        fh.close()
    writeSamples(upperHalf,
                 "upper_review_sentences",
                 4,
                 tigerFile)
    writeSamples(lowerHalf,
                 "lower_review_sentences",
                 16,
                 tigerFile)


def sample_summary(directory, tigerFile):
    print "running"
    sentences = []
    for fileName in glob.iglob(os.path.join(directory, "*.html.txt.split")):
        fh = open(fileName, "r")
        index = 0
        for sentence in fh.readlines():
            if sentence.startswith('Fazit:'):
                sentences.append((os.path.basename(fileName),
                                  index,
                                  sentence))
                index += 1
        fh.close()
    print "Found %s sentences" % len(sentences)
    writeSamples(sentences,
                 "fazit_samples",
                 20,
                 tigerFile)


def get_summaries(directory):
    sentences = []
    for fileName in glob.iglob(os.path.join(directory, "*.html.txt.split")):
        fh = open(fileName, "r")
        index = 0
        inFazit = False
        for sentence in fh.readlines():
            if sentence.startswith('Fazit:'):
                inFazit = True
            if inFazit:
                sentences.append((os.path.basename(fileName),
                                  index,
                                  sentence))
                index += 1
        fh.close()
    return sentences


def sample_summaries(directory, tigerFile):
    print "running"
    sentences = get_summaries(directory)
    print "Found %s sentences" % len(sentences)
    writeSamples(sentences,
                 "fazit_samples",
                 20,
                 tigerFile)

if __name__ == "__main__":
    sample(sys.argv[1], sys.argv[2])

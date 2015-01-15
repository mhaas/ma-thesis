#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import codecs
import sys
import re
import nltk

# This script uses the GermanPolarityClues data set to veto
# false or questionable 'objective' classification of phrases.
# The goal is a high-precision classifier.

whitelist = set([u'der', u'sein', u'dem', u'er'])

patternMap = {}
seen = set()

MLSA_SHIFTER_INTENSIFIER = False

stemmer = nltk.stem.snowball.GermanStemmer()


def read_mlsa(fileName):
    res = set()
    fh = codecs.open(fileName, 'r', 'utf-8')
    # - is negative, -_ is just a hypen
    if MLSA_SHIFTER_INTENSIFIER:
        pattern = re.compile(ur'\[?(\w+)(~|\^)\]?', re.UNICODE)
    else:
        pattern = re.compile(ur'\[?(\w+)(~|-[^_]|\+|\^)\]?', re.UNICODE)
    for line in fh.readlines():
        tokens = line.split(" ")
        for token in tokens:
            match = pattern.search(token)
            if match:
                word = match.group(1)
                if word in seen:
                    continue
                if word.lower() in whitelist:
                    continue
                print "got %s" % word
                word = stemmer.stem(word)
                print "Stemmed: %s" % word
                regex = compile_regex(word)
                res.add(regex)
                patternMap[regex] = word
                seen.add(word)
    return res


def compile_regex(token):
    # TODO: should work without \A and \Z
    return re.compile(ur'(\A|\b)' + re.escape(token) + ur'(\Z|\b)', re.UNICODE | re.IGNORECASE)


def read_gpc(fileName):
    global patternMap
    res = set()
    fh = open(fileName)
    r = csv.reader(fh, delimiter='\t')
    for row in r:
        feature = row[0].decode("utf-8")
        lemma = row[1].decode("utf-8")
        # compile into regexes once
        feature = stemmer.stem(feature)
        lemma = stemmer.stem(lemma)
        if (not feature in whitelist) or (feature in seen):
            regex = compile_regex(feature)
            patternMap[regex] = feature
            res.add(regex)
            seen.add(feature)
        if (not lemma in whitelist) or (lemma in seen):
            regex = compile_regex(lemma)
            patternMap[regex] = lemma
            res.add(regex)
            seen.add(lemma)
    fh.close()
    return res


def veto(fileName, blockers):
    acceptedFH = codecs.open(fileName + '.veto-accepted', 'w', 'utf-8')
    vetoedFH = codecs.open(fileName + '.veto-rejected', 'w', 'utf-8')
    logFH = codecs.open(fileName + '.log', 'w', 'utf-8')
    fh = codecs.open(fileName, 'r', 'utf-8')
    count = 0
    for line in fh.readlines():
        origLine = line
        line = line.strip()
        # no need for \n, origLine still has it
        logFH.write("Got line: %s" % origLine)
        line = stemmer.stem(line)
        logFH.write("Stemmed: %s\n" % line)
        vetoed = False
        # also need to look at invidual tokens,
        # as stemmer.stem('coolen Sprüchen') does not produce 'cool'
        tokens = line.split(' ')
        for blocker in blockers:
            if blocker.search(line):
                vetoed = True
                logFH.write(u'Veto: %s due to %s\n' % (line,
                                                       patternMap[blocker]))
            for token in tokens:
                token = stemmer.stem(token)
                if blocker.search(token):
                    vetoed = True
                    logFH.write(
                        'Veto for token: %s in line %s due to %s' % (token, line,
                                                                     patternMap[blocker]))
        if vetoed:
            count += 1
            vetoedFH.write(origLine)
            # no need for \n, origLine still has it
            # vetoedFH.write("\n")
        else:
            acceptedFH.write(origLine)
            # no need for \n, origLine still has it
            # acceptedFH.write("\n")
    logFH.write("Veto'ed %s\n" % count)
    acceptedFH.close()
    vetoedFH.close()
    logFH.close()
    fh.close()

if __name__ == "__main__":
    base = "/home/students/haas/ma/GermanPolarityClues/GermanPolarityClues-2012/"
    neg = read_gpc(base + "GermanPolarityClues-Negative-21042012.tsv")
    pos = read_gpc(base + "GermanPolarityClues-Positive-Lemma-21042012.tsv")
    #neg = set()
    #pos = set()
    mlsa = read_mlsa(
        "/home/students/haas/ma/mlsa/Layer2/layer2.phrases.majority.txt")
    neg.update(pos)
    neg.update(mlsa)
    veto(sys.argv[1], neg)

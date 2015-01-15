#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script converts downloaded movie reviews
# to the CQP vertical format.

import nltk
import os
import glob
import argparse
import re

sent_tokenizer = nltk.data.load('tokenizers/punkt/german.pickle')


def split_harder(sentences):
    u"""
    >>> split_harder([u'Ich mag Katzen.Du magst Kekse.'])
    [u'Ich mag Katzen.', u'Du magst Kekse.']
    >>> split_harder([u'Ich mag Katzen.Du magst Kekse.Wir lieben Eis.'])
    [u'Ich mag Katzen.', u'Du magst Kekse.', u'Wir lieben Eis.']
    >>> split_harder([u'4. Staffel sich wieder vermehrt'])
    [u'4. Staffel sich wieder vermehrt']
    >>> split_harder([u'Bild/Ton:Sehr gute,'])
    [u'Bild/Ton:Sehr gute,']
    """
    res = []
    # pattern is non-greedy so we get the first sentence
    # does not really matter in practice
    pattern = re.compile('(.*?(\w)+\.)((\w).*)', re.U)
    for sentence in sentences:
        match = pattern.match(sentence)
        if match:
            firstSentence = match.group(1)
            secondSentence = match.group(3)
            if pattern.match(firstSentence):
                sentences.append(firstSentence)
            else:
                res.append(firstSentence)
            if pattern.match(secondSentence):
                sentences.append(secondSentence)
            else:
                res.append(secondSentence)
        else:
            res.append(sentence)
    return res


def sentence_split(text, splitHarder):
    """Given a text, this returns a list of all sentences.
    >>> sentence_split(u'Er mag Filme. Sie mag Theater.', False)
    [u'Er mag Filme.', u'Sie mag Theater.']
    >>> sentence_split(u'Er mag Filme. Sie mag Theater.', True)
    [u'Er mag Filme.', u'Sie mag Theater.']
    >>> sentence_split(u'Er mag Filme. Sie mag Theater.Wir essen Kuchen.', False)
    [u'Er mag Filme.', u'Sie mag Theater.Wir essen Kuchen.']
    >>> sentence_split(u'Er mag Filme. Sie mag Theater.Wir essen Kuchen.', True)
    [u'Er mag Filme.', u'Sie mag Theater.', u'Wir essen Kuchen.']

    """
    sentences = sent_tokenizer.tokenize(text)
    if splitHarder:
        sentences = split_harder(sentences)
    return sentences


def main(inputFile, splitHarder):
    """Runs sentence splitter on files.

    The 'inputFile' argument must be a string pointing to a directory
    or to a file. The output file will have '.split' appended to its
    name.
    """
    files = [inputFile]
    if os.path.isdir(inputFile):
        files = glob.glob(os.path.join(inputFile, "*.txt"))
    for f in files:
        print "Processing file %s" % f
        outFile = open(f + ".split", "w")
        fh = open(f, "r")
        # clean up the replacements for <em> and <strong> so they do not get
        # tokenized
        text = fh.read().decode("utf-8")
        for sentence in sentence_split(text, splitHarder):
            outFile.write(sentence.encode("utf-8"))
            outFile.write("\n")
        outFile.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Transform text files into brown-clustering input format')
    parser.add_argument('--input', required=True,
                        help='input file or directory')
    parser.add_argument('--split-harder', required=False,
                        action='store_true',
                        help='Split hard cases "kaufen.Ich".')

    args = parser.parse_args()
    main(args.input, args.split_harder)

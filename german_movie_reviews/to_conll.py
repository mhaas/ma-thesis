#!/usr/bin/python
# -*- coding: utf-8 -*-

# This script converts downloaded movie reviews
# to the CQP vertical format.

import nltk
import os
import glob
import sys
import subprocess
import StringIO
import argparse

TOKENIZER = "/home/mitarb/versley/sources/cdec-2013-07-13/corpus/tokenize-anything.sh"


def sentence_split(text):
    """Given a text, this returns a list of all sentences."""
    sentences = sent_tokenizer.tokenize(text)
    return sentences


def tokenize_sentence_tb(sentence):
    """Tokenize sentence using NLTK implementation of the Penn Treebank
        tokenizer.
    >>> tokenize_sentence_tb(u"I like kittens.")
    [u'I', u'like', u'kittens', u'.']
    """
    tokenizer = nltk.tokenize.TreebankWordTokenizer()
    return tokenizer.tokenize(sentence)


def tokenize_sentence_cdec(sentence):
    """Given a single sentence, this returns a list of tokens."""
    #tokens = tokenizer.tokenize(sentence)
    buf = StringIO.StringIO(sentence)
    handle = subprocess.Popen(
        TOKENIZER, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    handle.stdin.write(sentence.encode("utf-8"))
    # send EOF
    handle.stdin.close()
    tokenized = handle.stdout.read()
    handle.poll()
    tokenized = tokenized.decode("utf-8")
    return tokenized.split(" ")


def main(inputFile, extension, splitter, tokenizer, strip_quotes=False):
    """Converts files to CONLL-style format for mate lemmatizer.

    The 'inputFile' argument must be a string pointing to a directory
    or to a file. The output file will be written to stdout.
    """
    files = [inputFile]
    if os.path.isdir(inputFile):
        files = glob.glob(os.path.join(inputFile, "*%s" % extension))
    for f in files:
        # print "Processing file %s" % f
        outFile = sys.stdout
        fileName = os.path.basename(f)
        fh = open(f, "r")
        # clean up the replacements for <em> and <strong> so they do not get
        # tokenized
        text = fh.read().decode("utf-8")
        for sentence in splitter.tokenize(text):
            if strip_quotes:
                sentence = sentence.replace('"', '')
            for token in tokenizer(sentence):
                outFile.write(token.encode("utf-8"))
                outFile.write(" ")
            outFile.write("\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Transform text files into CoNLL-style format.')
    parser.add_argument('--input', required=True,
                        help='input file or directory')
    parser.add_argument('--extension', required=True,
                        help='Extension, e.g. ".txt"')
    parser.add_argument('--strip-quotes', action='store_true')
    parser.add_argument('--sentence-splitter', choices=['cdec', 'treebank'],
                        required=True,
                        help="Use either cdec tokenize-anything.sh or NLTK TreebankWordTokenizer")
    parser.add_argument('--lang', choices=['EN', 'DE'],
                        required=True,
                        help='language of input data')

    args = parser.parse_args()
    if (args.lang == "EN"):
        splitter = nltk.data.load('tokenizers/punkt/english.pickle')
    else:
        splitter = nltk.data.load('tokenizers/punkt/german.pickle')
    if (args.sentence_splitter == "cdec"):
        tokenizer = tokenize_sentence_cdec
    else:
        tokenizer = tokenize_sentence_tb

    main(args.input, args.extension, splitter,
         tokenizer, strip_quotes=args.strip_quotes)

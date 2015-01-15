#!/usr/bin/python
# -*- coding: utf-8 -*-

# This script converts downloaded movie reviews
# to the CQP vertical format.

import nltk
import os
import glob
import argparse

GERMAN = 'DE'
ENGLISH = 'EN'

LATIN1 = 'latin-1'
UTF8 = 'utf-8'


class TextToBrownConverter(object):

    def __init__(self, language, enc):
        self.language = language
        if self.language == ENGLISH:
            self.sent_tokenizer = nltk.data.load(
                'tokenizers/punkt/english.pickle')
        elif self.language == GERMAN:
            self.sent_tokenizer = nltk.data.load(
                'tokenizers/punkt/german.pickle')
        else:
            raise ValueError('Unknown Language')
        # http://stackoverflow.com/a/15555162
        self.tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
        self.input_encoding = enc

    def sentence_split(self, text):
        """Given a text, this returns a list of all sentences."""
        sentences = self.sent_tokenizer.tokenize(text)
        return sentences

    def tokenize_sentence(self, sentence):
        """Given a single sentence, this returns a list of tokens."""
        tokens = self.tokenizer.tokenize(sentence)
        return tokens

    def main(self, inputFile, oneDocPerLine=False):
        """Converts files to Brown-Cluster input format.

        The 'inputFile' argument must be a string pointing to a directory
        or to a file. The output file will have '.brown_cluster' appended to
        itsname.
        """
        files = [inputFile]
        suffix = '.brown_input'
        if oneDocPerLine:
            suffix = '.tokenized'
        if os.path.isdir(inputFile):
            files = glob.glob(os.path.join(inputFile, "*.txt"))
        for f in files:
            print "Processing file %s" % f
            outFile = open(f + suffix, "w")
            fh = open(f, "r")
            text = fh.read().decode(self.input_encoding)
            documents = [text]
            if oneDocPerLine:
                documents = text.split('\n')
            idx = 0
            for document in documents:
                if oneDocPerLine:
                    # include document index
                    outFile.write('d%s ' % idx)
                sentences = self.sentence_split(document)
                for sentence in sentences:
                    for token in self.tokenize_sentence(sentence):
                        outFile.write(token.encode("utf-8"))
                        outFile.write(" ")
                    if not oneDocPerLine:
                        # remove last whitespace
                        outFile.seek(-1, 1)
                        # newline after each sentence
                        outFile.write('\n')
                if oneDocPerLine:
                    # remove last whitespace
                    outFile.seek(-1, 1)
                    # two newlines after each document
                    outFile.write('\n' * 2)
                idx += 1
            outFile.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Transform text files into brown-clustering input format')
    parser.add_argument('--input', required=True,
                        help='input file or directory')
    parser.add_argument('--one-document-per-line', required=False,
                        action='store_true',
                        help='One doc per line + doc ID (JST required)')
    parser.add_argument('--language', required=False,
                        choices=[ENGLISH, GERMAN],
                        default=GERMAN,
                        help='Language for Tokenizer')
    parser.add_argument('--input-encoding', required=False,
                        choices=[LATIN1, UTF8],
                        default=UTF8,
                        help='Input encoding.')
    args = parser.parse_args()
    o = TextToBrownConverter(args.language, args.input_encoding)
    o.main(args.input, args.one_document_per_line)

#!/usr/bin/python2
# -*- coding: utf-8 -*-

import secret
import csv
import sys
import argparse
import os
import glob
import re
import HTMLParser
from apiclient.discovery import build

import logging
logger = logging.getLogger("google-translate")
logging.basicConfig(filename='google-translate.log', level=logging.DEBUG)


def readText(sourceFile):
    """Reads regular text from file and yields lines."""
    fh = open(sourceFile, "r")
    lineNumber = 1
    for line in fh.readlines():
        line = line.decode("utf-8")
        # TODO: no need to normalize this
        #line = normalizeText(line)
        yield (lineNumber, line)
        lineNumber += 1
    fh.close()


def readSentimentTreeBank(sourceFile):
    """Reads tab-delimitted sentiment treebank file.

    Text will be de-tokenized by calling normalizeText().
    """
    fh = open(sourceFile, "r")
    reader = csv.reader(reader, delimiter="\t")
    # skip header
    reader.next()
    for row in reader:
        line = row[1].decode("utf-8")
        line = normalizeText(line)
        yield (int(row[0]), line)
    reader.close()


def normalizeText(line):
    """Normalizes text from Sentiment Treebank.

    Data from sentiment treebank is tokenized.
    Google translate prefers a non-tokenized version.

    # quoting is inconsistent due to the way the python interpreter handles this
    >>> normalizeText(u"The Rock is destined to be the 21st Century 's new `` Conan ''")
    u'The Rock is destined to be the 21st Century\\'s new "Conan"'
    >>> normalizeText(u"and that he 's going to make a splash even greater than Arnold Schwarzenegger , Jean-Claud Van Damme or Steven Segal .")
    u"and that he's going to make a splash even greater than Arnold Schwarzenegger, Jean-Claud Van Damme or Steven Segal."
    >>> normalizeText(u'-LRB- Wendigo is -RRB- why we go to the cinema : to be fed through the eye , the heart , the mind .')
    u'(Wendigo is) why we go to the cinema: to be fed through the eye, the heart, the mind.'
    >>> normalizeText(u'Between the drama of Cube ?')
    u'Between the drama of Cube?'
    >>> normalizeText(u'But what spectacular sizzle it is !')
    u'But what spectacular sizzle it is!'
    """
    possessiveRE = re.compile(u' \'s')
    line = possessiveRE.sub(u'\'s', line)
    startQuotesRE = re.compile(u'`` ')
    line = startQuotesRE.sub(u'"', line)
    endQuotesRE = re.compile(u' \'\'')
    line = endQuotesRE.sub(u'"', line)
    dotRE = re.compile(u' (\\.|,|:|\\?|!)')
    line = dotRE.sub(u'\\1', line)
    # space is optional, e.g. beginning of line, but if it is there,
    # we also put it in the replacement
    lrbRE = re.compile(u'-LRB- ')
    line = lrbRE.sub(u"(", line)
    rrbRE = re.compile(u' -RRB-')
    line = rrbRE.sub(u")", line)
    return line

service = build('translate', 'v2',
                developerKey=secret.KEY)


def translate(text, source, target):
    # Need to use unicode docstring to make unicode literals inside work
    u""" Translates text using Google Translate API.

    The api key must be in a file secret.py containing
    a declaration KEY=ABCDEFGD.

    Note that the tokenized english sentence does not work very well.

    >>> translate(u'Ich mag "Stirb Langsam"!', u'de', u'en')
    u'I like "Die Hard"!'
    >>> translate(u'Wird das Ergebnis ein verkapptes Rocky VII werden, obwohl Stallone 2006 beteuerte, dass nach Rocky Balboa endgültig Schluss ist?', u'de', u'en')
    u"Will the result be a capped Rocky VII, although Stallone in 2006 asserted that after Rocky Balboa's final conclusion?"
    >>> translate(u"A real movie , about real people , that gives us a rare glimpse into a culture most of us do n't know .", u'en', u'de')
    u"Ein echter Film \\xfcber echte Menschen, gibt uns einen seltenen Einblick in eine Kultur die meisten von uns wissen, dass n't."
    >>> translate(u"A real movie, about real people, that gives us a rare glimpse into a culture most of us don't know.", u'en', u'de')
    u'Ein echter Film \\xfcber echte Menschen, gibt uns einen seltenen Einblick in eine Kultur die meisten von uns nicht wissen, dass.'
    """
#    service = build('translate', 'v2',
#            developerKey=secret.KEY)
    # max 5000 characters per request.
    res = service.translations().list(
        source=source,
        target=target,
        q=text,
        format="text").execute()
    logger.debug("API response: %s", res)
    # res = {u'translations': [{u'translatedText': u'I like &quot;Die Hard&quot;!'}]}
    if not u'translations' in res:
        logger.error("No 'translation' member in response")
    if len(res[u'translations']) != 1:
        logger.error("Got response, but length of translations array is not 1")
    if not u'translatedText' in res[u'translations'][0]:
        logger.error("No member 'translatedText in response")
    translation = res[u'translations'][0][u'translatedText']
    return translation


def main(inFile, dataSource, source, target):
    """Translates input files from source language to target language.

    Input file can be a directory or a single file.
    Output files will have .translated appended to their name.
    """
    if os.path.isdir(inFile):
        files = glob.glob(os.path.join(inFile, "*.txt.split"))
    else:
        files = [inFile]

    for f in files:
        if os.path.exists(f + ".translated"):
            logger.info("File %s exists, skipping.", f + ".translated")
            continue
        out = open(f + ".translated.unfinished", "w")
        writer = csv.writer(out, delimiter="\t")
        writer.writerow(["line_index", "sentence"])
        for (lineNumber, line) in dataSource(f):
            translation = translate(line, source, target)
            writer.writerow([str(lineNumber), translation.encode("utf-8")])
        out.close()
        os.rename(f + ".translated.unfinished", f + ".translated")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Translate text using Google Translate.')
    parser.add_argument('--input', metavar='N', required=True,
                        help='input file or directory')
    parser.add_argument('--source', required=True,
                        help='source language')
    parser.add_argument('--target', required=True,
                        help='target language')
    parser.add_argument('--data-type', choices=['text', 'stanford'],
                        required=True,
                        help='format of input data')

    args = parser.parse_args()
    t = readText
    if (args.data_type == "stanford"):
        t = readSentimentTreeBank
    main(args.input, t, args.source, args.target)

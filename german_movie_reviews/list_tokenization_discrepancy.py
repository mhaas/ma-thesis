#!/usr/bin/python
# -*- coding: utf-8 -*-
import nltk
import sys
import os
import glob
import logging
import re


sent_tokenizer = nltk.data.load('tokenizers/punkt/german.pickle')

logger = logging.getLogger("list-tokenization-discrepancy")
logging.basicConfig(filename='list_tokenization_discrepancy.log',
                    level=logging.DEBUG)


def listFiles(targetDir, goldDir, targetAlreadyTokenized):
    if targetAlreadyTokenized:
        suffix = ".split"
    else:
        suffix = ""
    for fileName in glob.iglob(os.path.join(targetDir, "*.html.txt" + suffix)):
        base = os.path.basename(fileName)
        if targetAlreadyTokenized:
            other = os.path.join(goldDir, base[0:- len(suffix)])
        else:
            other = os.path.join(goldDir, base)
        logger.info("calling main(%s, %s)", fileName, other)
        main(fileName, other, targetAlreadyTokenized)


def tokensRoughlyEqual(t1, t2):
    # compare length of uncleaned
    # otherwise, we fail for files
    # where a quotation mark is on its own line
    if len(t1) != len(t2):
        return False
    t1 = map(clean, t1)
    t2 = map(clean, t2)
    if len(t1) != len(t2):
        return False
    for index in xrange(len(t1)):
        if not t1[index] == t2[index]:
            return False
    return False


def diffAlgo(quotedSentences, unquotedSentences, baseName,
             returnSplitOffset=False):
    res = []
    ql = len(quotedSentences)
    ul = len(unquotedSentences)
    ux = 0
    qx = 0
    logger.debug("diffAlgo: working on baseName: %s" % baseName)
    logger.debug("ql is %s, ul is %s", ql, ul)
    # TODO: sanity check: do we have same number of sentences AFTER merging?
    # TODO: checking for same number of sentences is silly,
    # better compare each one
    # while ux < ul:
    while qx < ql:
        # band-aid
        if ux >= ul:
            logger.debug("going over unquoted length")
            # if the ONLY difference is a final newline with a double quote
            # in quoted, we won't have r yet.
            r = (baseName, ql - 2, ql - 1)
            if not r in res:
                res.append(r)
            break
        logger.debug("Comparing at ux: %s ", ux)
        logger.debug(unquotedSentences[ux])
        logger.debug("to qx: %s", qx)
        logger.debug(quotedSentences[qx])

        if clean(unquotedSentences[ux]) != clean(quotedSentences[qx]):
            logger.info("Discrepancy found at index ux %s, qx %s", ux, qx)
            logger.info(clean(unquotedSentences[ux]))
            logger.info(clean(quotedSentences[qx]))
            if ux < (ul - 1):
                logger.debug("Scanning for next match")
                nextCandidate = unquotedSentences[ux + 1]
                nextQx = qx + 1
                if not nextQx < ql:
                    # this happens in one artificial test case
                    logger.warn("going over bounds of quoted sentence")
                    return res
                found = False
                while (nextQx) < ql:
                    # logger.debug("loop")
                    # prefix match is enough
                    # otherwise, the logic breaks if there are
                    # two subsequent sentences that are broken up
                    nc = clean(nextCandidate)[0:3]
                    qnc = clean(quotedSentences[nextQx])[0:3]
                    logger.debug("Comparing now: unquoted: %s, "
                                 + "quoted: %s", nc, qnc)
                    if nc == qnc:
                        found = True
                        res.append((baseName, qx, nextQx - 1))
                        logger.debug("Merge the following:")
                        for mergeCandidate in xrange(qx, nextQx):
                            logger.debug(quotedSentences[mergeCandidate])
                        qx = nextQx - 1
                        break
                    nextQx += 1
                if not found:
                    logger.warn("Huh? Could not find end of wrongly "
                                + "splitted sentence")
                    #logger.warn("Returning end...")
                    #res.append((baseName, qx, ql-1))
            else:
                logger.warn("Huh? at end of unquoted")
                res.append((baseName, qx, ql - 1))
        ux += 1
        qx += 1
    return res


def diff(quotedText, unquotedText, baseName, goldAlreadyTokenized):

    if goldAlreadyTokenized:
        quotedSentences = quotedText
    else:
        quotedSentences = sent_tokenizer.tokenize(quotedText)
    unquotedSentences = sent_tokenizer.tokenize(unquotedText)
    # logger.debug(quotedSentences)
    # logger.debug(unquotedSentences)
    res = {"MERGE": []}
    if not tokensRoughlyEqual(quotedSentences, unquotedSentences):
        res["MERGE"].extend(
            diffAlgo(quotedSentences, unquotedSentences, baseName))
    return res


def getBaseName(fileName):
    b = os.path.basename(fileName)
    regex = re.compile(ur"^(.+)\.html.txt.*$")
    match = regex.match(b)
    assert match
    return match.group(1)


def main(targetFile, goldFile, targetAlreadyTokenized):
    b1 = getBaseName(targetFile)
    b2 = getBaseName(goldFile)
    if b1 != b2:
        logger.error("file names not identical?! %s -- %s", b1, b2)
        assert False

    fh = open(targetFile, "r")
    if targetAlreadyTokenized:
        targetText = [x.decode("utf-8") for x in fh.readlines()]
    else:
        targetText = fh.read().decode("utf-8")
    fh.close()
    fh = open(goldFile, "r")
    goldText = fh.read().decode("utf-8")
    fh.close()
    r = diff(targetText, goldText, b1, targetAlreadyTokenized)
    logger.info(r)
    for (name, start, end) in r["MERGE"]:
        sys.stdout.write(("%s,%s,%s" % (name, start, end)).encode("utf-8"))
        sys.stdout.write("\n")


def clean(sentence):
    cleaned = sentence.replace('"', "").lower().strip()
    # logger.debug(cleaned)
    return cleaned

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description='Find sentence splitting differences between files.')
    parser.add_argument('--gold', required=True,
                        help='input directory from which differences '
                        + 'are extracted')
    parser.add_argument('--target', required=True,
                        help='input directory to which differences '
                        + 'eventually will be applied')
    parser.add_argument('--target-already-tokenized', action="store_true",
                        help='Assume target is already pre-tokenized: '
                        + 'once sentence per line')

    args = parser.parse_args()
    listFiles(args.target, args.gold, args.target_already_tokenized)

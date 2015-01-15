# -*- coding: utf-8 -*-
import re
import os
import nltk
import warnings

IDRE1 = re.compile(ur"(\d+)")
IDRE2 = re.compile(ur"^([a-zA-Z]*)(.*)$")


NEG = 0
NEU = 1
POS = 2

VERY_NEG = 0
SLIGHTLY_NEG = 1
FINE_NEU = 2
SLIGHTLY_POS = 3
VERY_POS = 4

GRANULARITY_COARSE = 'coarse'
GRANULARITY_FINE = 'fine'


def addOneS(s):
    """
    >>> addOneS("5")
    '6'
    >>> addOneS("foo3")
    'foo4'
    """
    def sub(matchobj):
        num = int(matchobj.group(1))
        return "%s" % (num + 1)
    return IDRE1.sub(sub, s)


def subtractOneS(s):
    """
    >>> subtractOneS("5")
    '4'
    >>> subtractOneS("foo3")
    'foo2'
    """
    def sub(matchobj):
        num = int(matchobj.group(1))
        return "%s" % (num - 1)
    return IDRE1.sub(sub, s)


def stripPrefixFromString(s):
    """
    >>> stripPrefixFromString("foo3")
    '3'
    >>> stripPrefixFromString("s400")
    '400'
    >>> stripPrefixFromString("s38560_n506BIN")
    '38560_n506BIN'
    >>> stripPrefixFromString("38560_40")
    '38560_40'
    """
    match = IDRE2.match(s)
    return match.group(2)


def strSen(val):
    """Returns integer representation of sentiment string.
    @param {string} Sentiment label
    @returns {int} Sentiment label as int
    """
    if val == "neg":
        return NEG
    elif val == "neu":
        return NEU
    elif val == "pos":
        return POS
    else:
        raise ValueError("Unknown sentiment: %s" % val)


def sen(projSentiment, granularity=GRANULARITY_COARSE):
    """Returns integer representation of fine-grained sentiment.
    If granularity is set to GRANULARITY_COARSE, then
    the method uses equivalence classes and collapses fine-grained
    labels [0,4] into coarses-grained NEG, NEU, POS.

    If granularity is set to GRANULARITY_FINE, then the
    labels are returned as-is.

    @param {string} Sentiment label
    @param {string} granularity Either GRANULARITY_COARSE or GRANULARITY_FINE
    @returns {int} Sentiment label as int.
    """
    if granularity == GRANULARITY_FINE:
        return int(projSentiment)
    elif granularity == GRANULARITY_COARSE:
        if projSentiment == "0" or projSentiment == "1":
            return NEG
        elif projSentiment == "2":
            return NEU
        elif projSentiment == "3" or projSentiment == "4":
            return POS
        else:
            raise ValueError("Unknown sentiment value %s" % projSentiment)
    else:
        raise ValueError("Unknown granularity %s" % granularity)


def walkTree(tree):
    """Walks NLTK tree in pre-order.
    Tree leaves are skipped as these do not have sentiment values.

    @param tree {nltk.trees.Tree} Tree be to traversed
    @yields {nltk.trees.Tree} Tree node
    """
    # skip leaves, these do not have sentiment values
    pos = tree.treepositions(order="preorder")
    for p in pos:
        if not hasattr(tree[p], "node"):
            continue
        yield tree[p]


def readPenn(treeBank, encoding='latin1'):
    """Reads parse trees from Penn Treebank file.

    @param treeBank {basestring} File name of treebank
    @param encoding {basestring} Encoding on disk
    @yields {nltk.trees.Tree} Parse tree
    """
    directory = os.path.dirname(treeBank)
    baseName = os.path.basename(treeBank)
    # Some NLTK 3.0 compat
    # if (type(nltk.corpus.reader.bracket_parse) == 'function'):
    #    corpus = nltk.corpus.reader.BracketParseCorpusReader(
    #        directory, baseName, detect_blocks='sexpr')
    # else:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        corpus = nltk.corpus.reader.bracket_parse.BracketParseCorpusReader(
            directory, baseName, detect_blocks='sexpr', encoding=encoding)
        for sentence in corpus.parsed_sents():
            yield sentence


def flipSentiment(label):
    if label == POS:
        return NEG
    elif label == NEG:
        return POS
    elif label == NEU:
        return NEU
    else:
        raise ValueError('Unknown sentiment value')


def serializeTrees(trees, outFile, encoding='latin1'):
    """
    Serializes parse trees to disk in Penn Treebank format.

    @param trees {list<trees>} List of trees
    @param encoding {basestring} Encoding on disk
    """
    out = open(outFile, "w")
    for tree in trees:
        # .encode('utf-8'))
        out.write(tree.pprint(margin=999999, nodesep='').encode(encoding))
        out.write('\n')
    out.close()

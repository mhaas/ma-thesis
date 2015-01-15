#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv
import shared.ma_util
import argparse
import nltk
from nltk.tag.stanford import POSTagger

stemmer = nltk.stem.snowball.GermanStemmer()


def read_cluster(clusterFile, lowerCase=False, stem=False):
    dictionary = {}
    fh = open(clusterFile)
    reader = csv.reader(fh, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        word = row[0].decode('utf-8')
        if lowerCase:
            word = word.lower()
        if stem:
            word = stemmer.stem(word)
        clusterID = row[1].decode('utf-8')
        dictionary[word] = clusterID
    fh.close()
    print "Read %s words in %s clusters" % (len(set(dictionary.keys())),
                                            len(set(dictionary.values())))
    return dictionary


def main(clusterFile, ptbFile, outFile, lowerCase, stem, posTags):
    tokensNotFound = set()
    totalNotFound = 0
    base = "/resources/processors/tagger/stanford-postagger-3.0/"
    posTagger = POSTagger(base + "/models/german.tagger",
                          base + "/stanford-postagger.jar")
    dictionary = read_cluster(clusterFile, lowerCase, stem)
    temp = []
    print "reading trees from %s" % ptbFile
    trees = shared.ma_util.readPenn(ptbFile)
    for tree in trees:
        temp.append(tree)
    trees = temp
    print "Finished reading trees"
    outFile = open(outFile, 'w')
    if posTags:
        posTags = map(lambda x: x.upper()[0], posTags)
        sentences = []
        for tree in trees:
            sentences.append(tree.leaves())
        taggedSentences = posTagger.batch_tag(sentences)
        assert len(taggedSentences) == len(sentences)
    sentenceIndex = 0
    for tree in trees:
        tokenIndex = 0
        for subTree in shared.ma_util.walkTree(tree):
            if len(subTree) == 1:
                child = subTree[0]
                if posTags:
                    taggedSentence = taggedSentences[sentenceIndex]
                    tagInitial = taggedSentence[tokenIndex][1][0]
                    print tagInitial
                if isinstance(child, basestring):
                    # is unicode already
                    subTree[0] = child
                    child = subTree[0]
                    if lowerCase:
                        child = child.lower()
                    if stem:
                        child = stemmer.stem(child)
                    # hum, we used to always look up a str in a map of unicode
                    # objects. this only works because we never see
                    # anything but ascii in the clusters..
                    tokenIndex += 1
                    if posTags and not tagInitial in posTags:
                        continue
                    clusterID = dictionary.get(child)
                    if not clusterID:
                        print "Cluster not found for %s" % child.encode('utf-8')
                        tokensNotFound.add(child)
                        totalNotFound += 1
                    else:
                        subTree[0] = clusterID
        outFile.write(tree.pprint(margin=999999, nodesep='').encode('utf-8'))
        outFile.write('\n')
        sentenceIndex += 1
    print "Tokens not found: %s" % totalNotFound
    print "Unique tokens not found: %s" % len(tokensNotFound)
    outFile.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--clusters', required=True,
                        help='File containing clusters.')
    parser.add_argument('--ptb-input', required=True,
                        help='PTB file to which clusters are applied')
    parser.add_argument('--ptb-output', required=True,
                        help='Output file for PTB with clusters applied')
    parser.add_argument('--lower-case', required=False,
                        action='store_true',
                        help='Lower-case words before matching.')
    parser.add_argument('--stem', required=False,
                        action='store_true',
                        help='Output file for PTB with clusters applied')
    # TODO: exclude
    parser.add_argument('--only-pos-tags', required=False,
                        action='append',
                        help='POS Tag Initials for which clusters are applied'
                        + ' (e.g. V, N, A..)')
    args = parser.parse_args()

    main(args.clusters, args.ptb_input, args.ptb_output, args.lower_case,
         args.stem, args.only_pos_tags)

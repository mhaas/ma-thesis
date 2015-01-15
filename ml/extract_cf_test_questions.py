#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import csv
import os


# This script attempts to extract positive and negative
# phrases from SentiWS. The output must be manually reviewed.

def read_sentiWS(fileName):
    """Reads SentiWS file into a dict.

    Each word form becomes a dict key,
    the weight becomes the corresponding value.

    @param fileName {str} the path to the SentiWS file
    @returns {dict} Mapping from word form to weight
    """
    res = []
    fh = open(fileName)
    r = csv.reader(fh, delimiter='\t')
    for row in r:
        tokenPos = row[0].split("|")
        token = tokenPos[0]
        pos = tokenPos[1]
        val = float(row[1])
        forms = [token]
        for form in forms:
            form = form.decode("utf-8")
            form = form.lower()
            res.append((form, val, pos))
    res.sort(key=lambda x: x[1], reverse=('Pos' in os.path.basename(fileName)))
    return res


def get_combinations(data):
    res = []
    for (form1, val1, pos1) in data:
        for (form2, val2, pos2) in data:
            if pos1 == "ADJX" and pos2 == "NN":
                res.append((form1, form2))
    return res


def get_best_adj_nn(data):
    adj = []
    nn = []
    for (form, val, pos) in data:
        if pos == "ADJX":
            adj.append(form)
        elif pos == "NN":
            nn.append(form)
    return (adj, nn)


def printtostdout(foo):
    for item in foo:
        sys.stdout.write(item.encode("utf-8"))
        sys.stdout.write("\n")


def main(positive, negative):
    p = read_sentiWS(positive)[300:]
    n = read_sentiWS(negative)[300:]
    pAdj, pNN = get_best_adj_nn(p)
    print "== Positive Adjectives =="
    printtostdout(pAdj)
    print "== Positive Nouns =="
    printtostdout(pNN)
    nAdj, nNN = get_best_adj_nn(n)
    print "== Negative Adjectives =="
    printtostdout(nAdj)
    print "Negative Nouns"
    printtostdout(nNN)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

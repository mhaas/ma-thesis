#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ma_util
import evaluate_productions
import sys


def main(treeFile):
    dump = set(['4 -> 1 3',
               '0 -> 1 3'])
    prods = {}
    pe = evaluate_productions.ProdEvaluator(True, ma_util.GRANULARITY_FINE)
    for tree in ma_util.readPenn(treeFile):
        for subTree in ma_util.walkTree(tree):
            l = pe.getInterestingLabel(subTree)
            if l:
                if not l in prods:
                    prods[l] = set()

                prod = '%s -> %s %s' % (subTree.node, subTree[0].node,
                                              subTree[1].node)
                prods[l].add(prod)
                if prod in dump:
                    print "DESIRED: %s" % l
                    print subTree.pprint().encode('utf-8')
                # don't print everything
                if len(subTree.leaves()) < 5:
                    print "L: %s" % l
                    print subTree.pprint().encode('utf-8')
    print "-" * 8
    for rule in prods:
        print "RULE: %s" % rule
        for prod in prods[rule]:
            print prod
        print "=" * 8

if __name__ == '__main__':
    print main(sys.argv[1])

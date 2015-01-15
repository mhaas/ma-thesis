#!/usr/bin/env python
# -*- coding: utf-8 -*-

import itertools

F = "POISON"

from shared import ma_util
from sklearn.metrics import precision_score
import argparse


class ProdEvaluator(object):

    def __init__(self, interesting=False,
                 granularity=ma_util.GRANULARITY_FINE):
        self.interesting = interesting
        self.granularity = granularity
        self.correct = {}
        self.incorrect = {}
        self.total = {}
        self.gold = []
        self.predicted = []
        self.correctI = {}
        self.incorrectI = {}
        self.totalI = {}
        self.goldI = []
        self.predictedI = []

    def count(self, goldProd, predProd):
        if not goldProd in self.total:
            self.total[goldProd] = 0
        self.total[goldProd] += 1
        if goldProd == predProd:
            if goldProd not in self.correct:
                self.correct[goldProd] = 0
            self.correct[goldProd] += 1
        else:
            if goldProd not in self.incorrect:
                self.incorrect[goldProd] = 0
            self.incorrect[goldProd] += 1

    def countI(self, goldL, predL):
        if not goldL in self.totalI:
            self.totalI[goldL] = 0
        self.totalI[goldL] += 1
        if goldL == predL:
            if goldL not in self.correctI:
                self.correctI[goldL] = 0
            self.correctI[goldL] += 1
        else:
            if goldL not in self.incorrectI:
                self.incorrectI[goldL] = 0
            self.incorrectI[goldL] += 1

    def getInterestingLabel(self, treeNode):
        """
        Finds 'interesting things' such as inversions, shifters,
        etc.
        """
        if len(treeNode) < 2:
            return None
        if self.granularity == ma_util.GRANULARITY_COARSE:
            raise NotImplementedError(
                'getInterestingLabels does not handle coarse labels!')
        catP = ma_util.sen(treeNode.node, self.granularity)
        catL = ma_util.sen(treeNode[0].node, self.granularity)
        catR = ma_util.sen(treeNode[1].node, self.granularity)
        if catP == catL and catP == catR:
            return "ID"
        cat_max = max(catL, catR)
        cat_min = min(catL, catR)
        cat_avg = (catL + catR) / 2.0
        # cat_miv is low if max sentiment is very POS
        cat_miv = ma_util.VERY_POS - cat_max
        # cat_mav is low if min sentiment is very POS
        cat_mav = ma_util.VERY_POS - cat_min
        if catP <= cat_max and catP >= cat_min:
            r_label = 'AVG'
        # is parent less positive than most positive child
        # and more positive than least positive?
        elif catP <= cat_mav and catP >= cat_miv:
            r_label = 'INV'
        elif catL == ma_util.FINE_NEU and ((catP - ma_util.FINE_NEU)
                                           * (catR - ma_util.FINE_NEU) < 0):
            #r_label = 'INV/L'
            r_label = 'INV'
        elif catR == ma_util.FINE_NEU and ((catP - ma_util.FINE_NEU)
                                           * (catL - ma_util.FINE_NEU) < 0):
            #r_label = 'INV/R'
            r_label = 'INV'
        elif (catP - ma_util.FINE_NEU) * (cat_avg - ma_util.FINE_NEU) > 0:
            # (3 (4 wundervollen) (2 Szenen)) would match
            # here, but other rules fire first
            # Also not sure if there is intensification happening there?
            r_label = 'INT'
        else:
            #r_label = '???'
            r_label = "MWE"
        return r_label

    def getProduction(self, treeNode):
        """
        >>> pe = ProdEvaluator()
        >>> from nltk.tree import Tree
        >>> t = Tree(3, [Tree(3, "good"), Tree(2, "movie")])
        >>> pe.getProduction(t)
        (3,3,2)
        >>> t = Tree(3, "good")
        >>> pe.getProduction(t)
        None
        """
        # If the tree is binary, then its children are other tree instances
        # unary nodes only have for terminals and associated sentiment label
        if len(treeNode) < 2:
            return None
        top = ma_util.sen(treeNode.node, self.granularity)
        c0 = ma_util.sen(treeNode[0].node, self.granularity)
        c1 = ma_util.sen(treeNode[1].node, self.granularity)
        return (top, c0, c1)

    def handleTree(self, tree1, tree2):
        for (n1, n2) in itertools.izip_longest(ma_util.walkTree(tree1),
                                               ma_util.walkTree(tree2), fillvalue=F):
            if n1 == F or n2 == F:
                raise ValueError('Tree length not equal or other breakage')
            prod1 = self.getProduction(n1)
            prod2 = self.getProduction(n2)
            goldLabel = int(n1.node)
            predLabel = int(n2.node)
            if prod1:
                self.count(prod1, prod2)
                self.gold.append(prod1)
                self.predicted.append(prod2)
            if not self.interesting:
                return
            coarse_map = {ma_util.VERY_NEG: ma_util.NEG,
                          ma_util.SLIGHTLY_NEG: ma_util.NEG,
                          ma_util.VERY_POS: ma_util.POS,
                          ma_util.SLIGHTLY_POS: ma_util.POS}
            ruleLabel = self.getInterestingLabel(n1)
            if ruleLabel and goldLabel in coarse_map:
                if not ruleLabel in self.totalI:
                    self.totalI[ruleLabel] = 0
                self.totalI[ruleLabel] += 1
                if (predLabel in coarse_map and
                        coarse_map[goldLabel] == coarse_map[predLabel]):
                    if not ruleLabel in self.correctI:
                        self.correctI[ruleLabel] = 0
                    self.correctI[ruleLabel] += 1
            #interes1 = self.getInterestingLabel(n1)
            #interes2 = self.getInterestingLabel(n2)
            # if interes1:
                #self.countI(interes1, interes2)
                # self.goldI.append(interes1)
                # self.predictedI.append(str(interes2))

    def main(self, treeFile1, treeFile2):
        trees1 = ma_util.readPenn(treeFile1)
        trees2 = ma_util.readPenn(treeFile2)
        for (t1, t2) in itertools.izip_longest(trees1, trees2, fillvalue=F):
            if t1 == F or t2 == F:
                raise ValueError('Tree length not equal or other breakage')
            self.handleTree(t1, t2)
        self.printSummary(self.total, self.correct, self.gold, self.predicted)
        if self.interesting:
            self.printSummary(self.totalI, self.correctI)

    def printSummary(self, total, correct, gold=None, predicted=None):
        buf = []
        for (prod, count) in total.iteritems():
            if prod in correct:
                correctCount = correct[prod]
            else:
                correctCount = 0
            precision = correctCount / float(count)
            buf.append((prod, precision, correctCount, count))
        print "Hardest rules first:"
        sortedList = sorted(buf, key=lambda x: (x[1], x[3]))
        for (prod, precision, correctCount, count) in sortedList:
            if isinstance(prod, tuple):
                readable = "%s => %s %s" % prod
            else:
                readable = prod
            print ("%s: %.3f Precision (%3s Correct, %3s Total)"
                   % (readable,
                      precision,
                      correctCount,
                      count))
        if gold and predicted:
            print ("Micro Avg precision: %.5f" % precision_score(gold,
                                                                 predicted,
                                                                 average='micro'))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--gold', required=True)
    parser.add_argument('--predicted', required=True)
    parser.add_argument('--find-interesting',
                        action='store_true')
    parser.add_argument('--granularity', required=True,
                        choices=[ma_util.GRANULARITY_COARSE,
                                 ma_util.GRANULARITY_FINE])
    args = parser.parse_args()
    pe = ProdEvaluator(args.find_interesting, args.granularity)
    pe.main(args.gold, args.predicted)

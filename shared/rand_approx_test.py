#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import evaluate
import argparse
#import sys
import ma_util
R = 1000


def randomize(resultsA, resultsB):
    assert len(resultsA) == len(resultsB)
    for index in xrange(len(resultsA)):
        if random.choice([True, False]):
            tmp = resultsA[index]
            resultsA[index] = resultsB[index]
            resultsB[index] = tmp
    return (resultsA, resultsB)


def t(gold, resultsA, resultsB, someStatistic):
    # compute difference in statistic between resultsA
    # and resultsB
    statA = someStatistic(gold, resultsA)
    statB = someStatistic(gold, resultsB)
    return abs(statA - statB)


def estimate_significance_level(gold, resultsA, resultsB, someStatistic):
    delta = t(gold, resultsA, resultsB, someStatistic)
    # The number of times that differences for randomized are >= than for
    # original
    r = 0
    for run in xrange(R):
        # if run % 100 == 0:
        #    print >> sys.stderr, "At iteration %s" % run
        copyA = list(resultsA)
        copyB = list(resultsB)
        randomA, randomB = randomize(copyA, copyB)
        randDelta = t(gold, randomA, randomB, someStatistic)
        if randDelta >= delta:
            r += 1
    significance = (r + 1) / float(R + 1)
    return significance


def approximate_randomization_test(gold, resultsA, resultsB, someStatistic,
                                   sigLevel):
    """
    Returns True if null hypothesis is rejected.
    """
    significance = estimate_significance_level(
        gold, resultsA, resultsB, someStatistic)
    print "p = %.10f" % significance
    if significance <= sigLevel:
        # print ('Null hypothesis rejected. Difference '
        #       + 'between systems is not due to chance.')
        return True
    else:
        # print ('Null hypothesis accepted. Difference '
        #       + 'between systems is pure chance.')
        return False

# End of the common part
# Now come the tree-specific parts


def rootAccStatistic(gold, predicted):
    # This looks somewhat convoluted - that's some legacy
    # from the CSV code.
    # combinedRootLabelAccMacro has always been used for root
    # accuracy. This method can be used to compute any
    # macro accuracy as 'root' is only symbolic,
    # but I only ever use it for root accuracy
    data = evaluate.printStatsCoarseInt(gold, predicted, prefix='root')
    return data['combinedRootLabelAccMacro']


def nodeF1Statistic(gold, predicted):
    data = evaluate.printStatsCoarseInt(gold, predicted)
    return data['combinedLabelFMacro']


def main(goldFile, resultsAFile, resultsBFile, sigLevel):
    (goldRoot,
     goldNodes) = evaluate.getTreeLabelsFile(goldFile,
                                             ma_util.GRANULARITY_COARSE)
    (aRoot,
     aNodes) = evaluate.getTreeLabelsFile(resultsAFile,
                                          ma_util.GRANULARITY_COARSE)
    (bRoot,
     bNodes) = evaluate.getTreeLabelsFile(resultsBFile,
                                          ma_util.GRANULARITY_COARSE)
    print "Testing: Root"
    rootIsSignificant = approximate_randomization_test(
        goldRoot, aRoot, bRoot, rootAccStatistic, sigLevel)
    if rootIsSignificant:
        print 'Difference for root accuracy is statistically significant.'
    print "Testing: Nodes"
    nodeIsSignificant = approximate_randomization_test(
        goldNodes, aNodes, bNodes, nodeF1Statistic, sigLevel)
    if nodeIsSignificant:
        print 'Difference for node f1 is statistically significant.'
    return (rootIsSignificant, nodeIsSignificant)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Perform randomized approximation test.')
    parser.add_argument('--gold', required=True,
                        help='Gold PTB file')
    parser.add_argument('--system-a', required=True,
                        help='System A output (PTB file)')
    parser.add_argument('--system-b', required=True,
                        help='System B output (PTB file)')
    parser.add_argument('--p', required=True,
                        type=float, help='Significance Level.')

    args = parser.parse_args()
    main(args.gold, args.system_a, args.system_b, args.p)

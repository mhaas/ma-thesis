#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import itertools
import tigerhelper as th
import shared.evaluate
import shared.deprecated
import shared.ma_util


@shared.deprecated.deprecated
def moreStats(goldLabels, predictedLabels, desiredClass):
    return shared.evaluate.morestats(goldLabels, predictedLabels, desiredClass)


@shared.deprecated.deprecated
def printStats(goldLabels, predictedLabels, showPercentages,
               prefix=None):
    return shared.evaluate.printStats(goldLabels, predictedLabels,
                                      showPercentages, prefix=None)


def mapNumToS(label):
    return shared.evaluate.mapNumericsToSentiment([label])[0]


def evaluate(predictFile, goldFile,
             showPercentages, dumpFile, csvFile, runName):
    if dumpFile is not None:
        dumpFile = open(dumpFile, "w")
    rootPredictedLabels = []
    rootGoldLabels = []
    predictedLabels = []
    goldLabels = []
    mappedPredictedLabels = []
    mappedGoldLabels = []
    predictTiger = th.TigerHelper(predictFile)
    predictSentences = th.getSentences(predictTiger.tree)
    gold = shared.ma_util.readPenn(goldFile)
    for (predictSentence,
         goldSentence) in itertools.izip_longest(predictSentences,
                                                 gold,
                                                 fillvalue=
                                                 "LIST_LENGTH_NOT_EQUAL"):
        rootPredictedLabels.append(predictTiger.getSentenceSentiment(
            predictSentence, forceSentiment=True))
        rootGoldLabels.append(goldSentence.node)
        # print "#" * 16
        for (predictNode, goldNode) in itertools.izip_longest(
                predictTiger.preOrder(predictSentence, forceSentiment=True),
                shared.ma_util.walkTree(goldSentence),
                fillvalue="LIST_LENGTH_NOT_EQUAL"):
            predictedSentiment = predictNode[1]
            #if (predictedSentiment is None):
                #print predictNode
            predictedLabels.append(predictedSentiment)
            # print "=" * 8
            # print goldNode
            # print "-" * 8
            # print predictNode
            # print "=" * 8
            goldSentiment = goldNode.node
            goldLabels.append(goldSentiment)
            if predictNode[2] != th.SEN_DEFAULT:
                mappedPredictedLabels.append(predictedSentiment)
                mappedGoldLabels.append(goldSentiment)
            if dumpFile and (mapNumToS(predictedSentiment)
                             != mapNumToS(goldSentiment)):
                dumpFile.write("=" * 8)
                dumpFile.write("\n")
                dumpFile.write("Prediction error.\n")
                dumpFile.write("gold: ")
                dumpFile.write(str(goldNode))
                dumpFile.write("\n")
                dumpFile.write("predicted:")
                dumpFile.write(str(predictNode[1]))
                dumpFile.write("\n")
                dumpFile.write("=" * 8)
                dumpFile.write("\n")
    if dumpFile is not None:
        dumpFile.close()
    print "All node labels"
    allNodes = printStats(goldLabels, predictedLabels,
                          showPercentages)
    print ""
    print "Mapped node labels only (No default)"
    noDefault = printStats(mappedGoldLabels, mappedPredictedLabels,
                           showPercentages, prefix="noDefault")
    print "Skipped %s default labels" % (len(goldLabels)
                                         - len(mappedGoldLabels))
    print ""
    print "Root labels"
    rootLabels = printStats(rootGoldLabels, rootPredictedLabels,
                            showPercentages, prefix="root")

    allNodes = shared.evaluate.ins(['run', "type"], [runName, "all nodes"],
                                   allNodes)
    noDefault = shared.evaluate.ins(['run', 'type'], [runName, "no default"],
                                    noDefault)
    allNodes.update(rootLabels)
    shared.evaluate.statsToFile(allNodes, csvFile)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Evaluate sentiment predictions against a gold standard.')
    parser.add_argument('--predicted', required=True,
                        help='PTB file with predicted sentiment labels.')
    parser.add_argument('--gold', required=True,
                        help='PTB file with gold sentiment labels.')
    parser.add_argument("--map-to-sentiment", action="store_true",
                        help="Maps numeric sentiment values [0,4] to"
                        + " [neg, neu, pos]. Always on, can't be disabled!")
    parser.add_argument("--show-percentages", action="store_true",
                        help="Shows percentages in confusion matrix.")
    parser.add_argument("--dump", required=False,
                        help="Dump incorrectly classified segments to file.")
    parser.add_argument("--csv-file", required=True,
                        help="Write evaluation data to CSV file.")
    parser.add_argument("--run-name", required=True,
                        help="Name of the run")
    args = parser.parse_args()
    evaluate(args.predicted, args.gold, args.map_to_sentiment,
             args.show_percentages, args.dump, args.csv_file, args.run_name)

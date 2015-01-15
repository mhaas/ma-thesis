#!/usr/bin/env python


import sys
import csv
import os
from evaluate_coef_sentiment_prediction import PhrasePredictor
from scripts.apply_cluster_to_ptb import read_cluster
from sklearn.ensemble import GradientBoostingClassifier
from feature_extraction import SentiWSExtractor
import shared.ma_util


# This script trains an ensemble clasifier based on SentiWs
# and MZN dictionary features.
# The classifier is used to classify words in clusters into sentiment
# categories.
# The clusters will be divided into sub-clusters based on
# prior sentiment polarity of a word


base = os.environ.get('DATADIR')
if not base:
    print >> sys.stderr, "DATADIR not set in environment. Bailing out"
    sys.exit(-1)

modelBase = os.path.join(base, 'mzn-reg-models-wo-singletons')
key = 'f56da36cf010264035535def0ca31b2c'
alphabet = os.path.join(modelBase, 'alphabet_%s.pickle' % key)
model = os.path.join(modelBase, 'lassocv_%s.pickle' % key)
args = os.path.join(modelBase, 'args_%s.pickle' % key)
pp = PhrasePredictor(alphabet, model, args, False)

sentiPOS = os.path.join(base, '3rdparty/sentiws/SentiWS_v1.8c_Positive.txt')
sentiNEG = os.path.join(base, '3rdparty/sentiws/SentiWS_v1.8c_Negative.txt')
sentiWSE = SentiWSExtractor(pp, sentiPOS, sentiNEG)


def extract_features(token):
    (doc_score_sum, doc_score_model) = pp.main(token)
    (swn, swp) = sentiWSE.getSentiWSScore(token)
    return [doc_score_model, swp, swn]


def read_gold(inFile):
    # TODO: could use some POS magic
    data = []
    labels = []
    penn = shared.ma_util.readPenn(inFile)
    for tree in penn:
        leaves = tree.pos()
        for (word, sentiLabel) in leaves:
            features = extract_features(word)
            data.append(features)
            label = shared.ma_util.sen(sentiLabel)
            labels.append(label)
    return (data, labels)


def doCluster(classifier, clusterIn, clusterOut):
    res = {}
    clusters = read_cluster(clusterIn)
    for (word, clusterID) in clusters.iteritems():
        curFeature = extract_features(word)
        predictedLabel = classifier.predict([curFeature])[0]
        res[word] = str(predictedLabel) + clusterID[1:]
    outFH = open(clusterOut, 'w')
    for (word, clusterID) in res.iteritems():
        line = u"%s\t%s\n" % (word, clusterID)
        outFH.write(line.encode('utf-8'))
    outFH.close()


def doTokenList(classifier, tokenIn, tokenOut):
    res = []
    fh = open(tokenIn)
    tokens = fh.readlines()
    tokens = map(lambda x: x.strip().decode('utf-8'), tokens)
    for token in tokens:
        curFeature = extract_features(token)
        predictedLabels = classifier.predict_proba([curFeature])[0]
        line = [token.encode('utf-8')]
        line.extend(predictedLabels)
        res.append(line)
    outFH = open(tokenOut, 'w')
    writer = csv.writer(outFH, delimiter='\t')
    for line in res:
        writer.writerow(line)
    outFH.close()


def main(goldFile, inFile, outFile, tokenList=False):
    (trainData, trainLabels) = read_gold(goldFile)
    classifier = GradientBoostingClassifier()
    classifier.fit(trainData, trainLabels)
    if tokenList:
        doTokenList(classifier, inFile, outFile)
    else:
        doCluster(classifier, inFile, outFile)
    # dictionary[word] = clusterID
    print "Feature importances for classifier"
    print ("MZN-Score-Reg | SentiWS-Pos | SentiWS-Neg")
    if not hasattr(classifier, 'feature_importances_'):
        print "Classifier does not have feature_importances_"
    else:
        weights = " | ".join(map(lambda x: "%.3f" % x,
                                 classifier.feature_importances_))
        print weights

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], True)

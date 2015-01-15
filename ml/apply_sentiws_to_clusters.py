#!/usr/bin/env python


from evaluate_coef_sentiment_prediction import PhrasePredictor
from scripts.apply_cluster_to_ptb import read_cluster
import feature_extraction
import sys

import os

# This script applies the SentiWS sentiment dictionary
# to a cluster file
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
extractor = feature_extraction.SentiWSExtractor(pp, sentiPOS, sentiNEG)


def score(word):
    negScore, posScore = extractor.getSentiWSScore(word)
    return (negScore + posScore)


def main(clusterIn, clusterOut):
    # dictionary[word] = clusterID
    clusters = read_cluster(clusterIn)
    res = {}
    for (word, clusterID) in clusters.iteritems():
        #(doc_score_sum, doc_score_model) = pp.main(word)
        #sentimentLabel = pp.score_sum_to_sentiment(doc_score_sum)
        sentiWSSum = score(word)
        if sentiWSSum < 0:
            label = "0"
        elif sentiWSSum == 0:
            label = "1"
        elif sentiWSSum > 0:
            label = "2"
        res[word] = label + clusterID[1:]

    outFH = open(clusterOut, 'w')
    for (word, clusterID) in res.iteritems():
        line = u"%s\t%s\n" % (word, clusterID)
        outFH.write(line.encode('utf-8'))
    outFH.close()

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

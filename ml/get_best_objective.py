#!/usr/bin/env python

import yaml
import itertools
import sys

OBJ = 1
SUBJ = 0

if __name__ == "__main__":
    fh = open(sys.argv[1])
    data = yaml.load(fh)
    fh.close()
    percentage = float(sys.argv[2])

    spans = data['spans']
    probs = data['probabilities']
    assert len(spans) == len(probs)
    res = []
    for (span, prob) in itertools.izip(spans, probs):
        probObj = prob[OBJ]
        probSubj = prob[SUBJ]
        # for ties, go with majority class: obj
        if probObj > probSubj:
            clazz = OBJ
        else:
            clazz = SUBJ
        res.append((span, clazz, abs(probObj - probSubj)))
    # sort by confidence
    res.sort(key=lambda x: x[2], reverse=True)
    cutoff = int(percentage * len(res))
    count100confident = 0
    remaining = res[:cutoff]
    objFH = open(sys.argv[3], 'w')
    subjFH = open(sys.argv[4], 'w')
    for (span, clazz, confidence) in remaining:
        if confidence == 1.0:
            count100confident += 1
        if clazz == OBJ:
            cl = "OBJ"
            objFH.write(span)
            objFH.write("\n")
        else:
            cl = "SUBJ"
            subjFH.write(span)
            subjFH.write("\n")
        print "%s: %s: %s" % (cl, confidence, span)
    print "100%% confident: %s out of %s" % (count100confident,
                                             len(remaining))
    objFH.close()
    subjFH.close()

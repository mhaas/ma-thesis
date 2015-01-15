#!/usr/bin/env python
# -*- coding: utf-8 -*-


import csv
import sys
import collections


def get_sentiment_for_duplicates(fileName):
    res = {}
    sentiments = {}
    fh = open(fileName)
    reader = csv.DictReader(fh)
    for row in reader:
        identifier = row['_unit_id']
        segment = row['content'].strip()
        sentiment = row['sentiment']
        if not segment in res:
            res[segment] = [identifier]
        if not segment in sentiments:
            sentiments[segment] = []
        sentiments[segment].append(sentiment)
        if not identifier in res[segment]:
            print ("Found identical segment '%s' with different ID (%s != %s)!"
                   % (segment, res[segment], identifier))
            print "Sentiment values: %s" % sentiments[segment]
            res[segment].append(identifier)
    print "-" * 16
    duplicates = {}
    for (phrase, identifiers) in res.iteritems():
        if len(identifiers) > 1:
            print "Duplicate identifiers: %s" % identifiers
            sentiment = sentiments[phrase]
            s = collections.Counter(sentiment)
            print "Sentiment: %s" % sentiment
            most_freq_sentiment = s.most_common(1)[0][0]
            print "Most frequent sentiment: %s" % s.most_common(1)[0][0]
            for identifier in identifiers:
                duplicates[identifier] = (phrase, most_freq_sentiment)
    fh.close()
    return duplicates

def filter_duplicates(aggregateFileName, outFileName, duplicates):
    fh = open(aggregateFileName)
    reader = csv.DictReader(fh)
    outFH = open(outFileName, 'w')
    writer = csv.writer(outFH, delimiter='\t', quoting=csv.QUOTE_NONNUMERIC)
    for row in reader:
        identifier = row["_unit_id"]
        segment = row['content'].strip()
        sentiment = row['sentiment']
        if identifier not in duplicates:
            writer.writerow([segment, int(sentiment)])
        else:
            print "Got duplicate %s, skipping!" % identifier
    for (phrase, sentiment) in set(duplicates.values()):
        writer.writerow([phrase, int(sentiment)])
    fh.close()
    outFH.close()

if __name__ == "__main__":
    duplicates = get_sentiment_for_duplicates(sys.argv[1])
    filter_duplicates(sys.argv[2], sys.argv[3], duplicates)

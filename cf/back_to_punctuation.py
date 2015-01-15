#!/usr/bin/env python
# -*- coding:utf-8 -*-

import csv
import codecs
import re
import sys


def read_tsv(fileName):
    res = []
    fh = open(fileName)
    r = csv.reader(fh, delimiter='\t')
    for row in r:
        phrase = row[0].decode('utf-8')
        sentiment = int(row[1].decode('utf-8'))
        regex = make_regex(phrase)
        res.append((phrase, regex, sentiment))
    fh.close()
    return res


def read_segments(fileName):
    res = []
    fh = codecs.open(fileName, 'r', 'utf-8')
    for line in fh.readlines():
        line = line.strip()
        res.append(line)
    fh.close()
    return res


def make_regex(phrase):
    """
    >>> reg = make_regex(u'aber absolut lustig , seh')
    >>> assert reg.match(', aber absolut lustig , seh')
    True
    """
    # orig call
    # sed -e 's/^ //g'  $target/remaining_remaining.segments | sed -e 's/ $//g'
    # | sed -r -e "s/^(,|.|'') //g" | sed -r -e "s/ (,|.|'')$//g"
    escaped = re.escape(phrase)
    # need to escape the '.'
    # or we will match "beides" to "beide"
    #punctuation = ur"(,|\.|'')?"
    # we accidentally remove question marks
    # sed -r -i -e 's/ ?$/"/' $target/phrases_unannotated.txt
    # Oops, we accidentally remove any character
    # But this should mainly be punctuation..
    # sed -e 's/^ //g'  $target/remaining_remaining.segments | sed -e 's/
    #     $//g' | sed -r -e "s/^(,|.|'') //g" | sed -r -e "s/ (,|.|'')$//g"  |
    #     sort -u \
    # so consider the following a list of what we removed and what we're adding
    # back
    # some overgeneration won't hurt - AnnotationToPTB will ignore
    # extraneous entries
    # "I 'll" is for "I 'll be back" - the regex is more specific
    # than the others to avoid false positives
    punctuation = ur"(,|\.|''|\?|-|:|`|3|&|!|2|5|1|7|6|'|I)?"

    regex = (ur'^' + punctuation + ur' ?' + escaped + ' ?'
             + punctuation + ur'\??$')
    return re.compile(regex)


def match(origSegments, annotatedTSV, outFile):
    annotated = read_tsv(annotatedTSV)
    segments = read_segments(origSegments)
    annotatedSet = set(map(lambda x: x[0], annotated))
    outFH = open(outFile, 'w')
    outWriter = csv.writer(outFH, delimiter='\t', quoting=csv.QUOTE_NONNUMERIC)
    matchedSegments = set()
    for (phrase, regex, sentiment) in annotated:
        matched = False
        prevMatch = None
        for segment in segments:
            # skip if phrase and segment are exactly equal
            # we print the phrase later on
            if phrase == segment:
                continue
            if regex.match(segment):
                if matched:
                    print "Huh? Got two matches? Something is probably wrong"
                    print ("Double match: '%s'\n'%s'\nprev segment: '%s'"
                           % (phrase, segment, prevMatch))
                    print "-" * 16
                matched = True
                prevMatch = segment
                #print ("Got match: annotated phrase %s matched segments %s" %
                #       (phrase, segment))
                # TODO: check for leading and trailing whitespace
                if segment in annotatedSet:
                    print "RegEx matches, but we already have this segment in the annotated data"
                # write no segment twice
                elif segment in matchedSegments:
                    print "We have matched this segment already, so we're skipping it"
                else:
                    outWriter.writerow([segment.encode('utf-8'), sentiment])
                    matchedSegments.add(segment)
        outWriter.writerow([phrase.encode('utf-8'), sentiment])
    outFH.close()


if __name__ == "__main__":
    match(sys.argv[1], sys.argv[2], sys.argv[3])

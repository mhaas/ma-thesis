#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Prepares a file for upload to CrowdFlower.
# Given a list of segments which must be annotated
# and a list of segments which are already annotated,
# generates a CSV file which can be uploaded to CrowdFlower

import csv
import sys
import argparse

SKIPPATTERN = [',', '.', '\'\'']


def removePunctuation(segment):
    for pat in SKIPPATTERN:
        beginPattern = pat + ' '
        if segment.startswith(beginPattern):
            segment = segment[len(beginPattern):]
        endPattern = ' ' + pat
        if segment.endswith(endPattern):
            segment = segment[:-len(endPattern)]
    return segment


def readSegments(segmentsFile):
    """
    Reads the output of info.mhaas.ma.PTBHandling.ExtractSegments.
    """
    segments = set()
    fh = open(segmentsFile)
    for line in fh:
        segment = line.strip()
        if segment in segments:
            print >> sys.stderr, "Segment %s already seen" % segment
        # Replicate some original filtering
        #sed -e 's/^ //g'  $target/remaining_remaining.segments
        #| sed -e 's/ $//g'
        #| sed -r -e "s/^(,|.|'') //g"
        #| sed -r -e "s/ (,|.|'')$//g"
        #|  sort -u \
        # Note: this needs to be recovered with scripts/back_to_punctuation.py
        # segment = segment.strip()
        segment = removePunctuation(segment)
        segments.add(segment)
    fh.close()
    return segments


def readAnnotationFile(annotationFile):
    """
    Reads CSV files straight from CrowdFlower.
    """
    fh = open(annotationFile)
    reader = csv.DictReader(fh, delimiter=',')
    # _unit_id,_golden,_canary,_unit_state,_trusted_judgments
    # content
    annotatedSegments = set()
    for row in reader:
        content = row['content']
        unitState = row['_unit_state']
        if unitState == 'golden':
            print >> sys.stderr, 'Segment %s is gold, skipping' % content
            continue
        elif unitState == 'finalized':
            if content in annotatedSegments:
                print >> sys.stderr, ('Annotated segment %s seen before?!'
                                      % content)
            # add version with and without punctuation
            # just for a possible corner case where a version without
            # punctuation never got annotated
            annotatedSegments.add(content)
            annotatedSegments.add(removePunctuation(content))
        else:
            raise ValueError('Unknown unit state %s in file %s'
                             % (unitState, annotationFile))
    fh.close()
    return annotatedSegments


def makeCSV(notYetAnnotated, outFile):
    header = ['id', 'content', 'relevant_gold', 'relevant_gold_reason',
              'sentiment_gold', 'sentiment_gold_reason']
    index = 0
    fh = open(outFile, 'w')
    writer = csv.writer(fh, delimiter=',')
    writer.writerow(header)
    for segment in notYetAnnotated:
        row = [index, segment, '', '', '', '']
        index += 1
        writer.writerow(row)
    fh.close()


def main(segmentsFile, annotationFiles, outFile):
    segments = readSegments(segmentsFile)
    annotations = set()
    for annotationFile in annotationFiles:
        annotations.update(readAnnotationFile(annotationFile))
    notYetAnnotated = segments - annotations
    print "All segments: %s" % len(segments)
    print "Already annotated: %s" % len(annotations)
    print "Not yet annotated: %s" % len(notYetAnnotated)
    makeCSV(notYetAnnotated, outFile)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Creates CrowdFlower CSV file')
    parser.add_argument('--segments', required=True,
                        help='All segments from parse trees')
    parser.add_argument('--annotation', action='append',
                        required=False,
                        help='Pre-existing annotations. May be specified'
                        + ' multiple times')
    parser.add_argument('--out', required=True,
                        help='Output file name.')
    args = parser.parse_args()
    main(args.segments, args.annotation, args.out)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

START = '<review_text>'
END = '</review_text>'

import argparse
import random

# A 'pseudo-XML' structure.. very helpful.


def main(fileName, output, sample):
    """Dumps all review text in a single stream."""
    fh = open(fileName)
    currentReview = None
    currentlyInReview = False
    allReviews = []
    for line in fh:
        line = line.strip()
        if line == END:
            currentlyInReview = False
            allReviews.append(currentReview)
        if currentlyInReview:
            currentReview += line
            currentReview += '\n'
        if line == START:
            currentReview = ""
            currentlyInReview = True
    fh.close()
    if sample:
        reviews = random.sample(allReviews, sample)
    else:
        reviews = allReviews
    outFH = open(output, 'w')
    for review in reviews:
        outFH.write(review)
    outFH.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=('Dump review text from Multi-Domain Sentiment Dataset '
                     + '(Blitzer et al, 2007)'))
    parser.add_argument('--input', required=True,
                        help='A .review file from the dataset')
    parser.add_argument('--output', required=True,
                        help='Output file for the extracted text')
    parser.add_argument('--sample', required=False, type=int,
                        help=('Number of reviews to output.'
                              + ' Randomly sampled w/o replacement'))
    args = parser.parse_args()
    main(args.input, args.output, args.sample)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import evaluate
import argparse
import ma_util
import csv


def main(goldFile, predFile, outCSVFile):
    header = []
    data = []
    atN = evaluate.accuracyAtN(goldFile, predFile, ma_util.GRANULARITY_COARSE)
    for key in sorted(atN.keys()):
        header.append('Acc at %s' % key)
        data.append(atN[key][0])
        header.append('Support at %s' % key)
        data.append(atN[key][1])
    outFH = open(outCSVFile, 'w')
    writer = csv.writer(outFH)
    writer.writerow(header)
    writer.writerow(data)
    outFH.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Evaluate system output against a gold standard.')
    parser.add_argument('--gold', required=True,
                        help='Gold PTB file')
    parser.add_argument('--predicted', required=True,
                        help='System output (PTB file)')
    parser.add_argument('--output-file', required=True,
                        help='Where to store CSV results.')
    args = parser.parse_args()
    main(args.gold, args.predicted, args.output_file)

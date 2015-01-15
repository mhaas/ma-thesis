#!/usr/bin/env python
# -*- coding: utf-8 -*-

import evaluate
import argparse


def main(goldFile, predFile, outCSVFile, description, fieldName1, fieldValue1):
    (goldRoot, goldNodes) = evaluate.getCoarseGrainedTreeLabelsFile(goldFile)
    (predRoot, predNodes) = evaluate.getCoarseGrainedTreeLabelsFile(predFile)
    rootData = evaluate.printStatsCoarseInt(goldRoot, predRoot, prefix='root')
    nodeData = evaluate.printStatsCoarseInt(goldNodes, predNodes)
    nodeData.update(rootData)
    if description:
        nodeData = evaluate.ins(['Description'],
                                [description], nodeData)
    if fieldName1 and fieldValue1:
        nodeData = evaluate.ins([fieldName1],
                                [fieldValue1], nodeData)

    evaluate.statsToFile(nodeData, outCSVFile, delim=';')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Evaluate system output against a gold standard.')
    parser.add_argument('--gold', required=True,
                        help='Gold PTB file')
    parser.add_argument('--predicted', required=True,
                        help='System output (PTB file)')
    parser.add_argument('--output-file', required=True,
                        help='Where to store CSV results.')
    parser.add_argument('--description', required=False,
                        help='Description of this run')
    parser.add_argument('--extra-field-name', required=False,
                        help='Extra field to add in the CSV file.')
    parser.add_argument('--extra-field-value', required=False,
                        help='Value of the extra field')
    args = parser.parse_args()
    main(args.gold, args.predicted, args.output_file,
         args.description, args.extra_field_name, args.extra_field_value)

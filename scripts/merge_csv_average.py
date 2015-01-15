#!/usr/bin/env python

import os
import os.path
import csv
import sys

# This script merges evaluation results for different splits
# and stores the output in all.csv


def main(dirName, filePattern, delimiter, skipFirstRow, skipNonFloatCol,
         outFileName='all.csv'):
    """
    This script is intended to merge results from single folds of a
    cross-validation experiment into a single CSV file.
    Individual measurements across all fold are averaged.

    The filePattern must contain a string replacement %s where the fold
    number will be supported. The script only supports 10-fold
    cross-validation.
    If you pass filePattern='all_%s.csv', then files all_0.csv, all_1.csv,...,
    all_9.csv will be opened.

    If only the first CSV file has a header, set the skipFirstRow parameter
    to true.

    If the CSV file contains some columns which cannot be averaged, such as a
    run name, then specify these in a list and pass it to skipNonFloatCol.
    The value for this column in the resulting file is copied from the first
    fold.

    @param dirName {string} Directory to search to CSV files
    @param filePattern {string} File name pattern, must contain %s for fold
    @param delimiter {string} Column delimiter, e.g. ';' or ','
    @param skipFirstRow {bool} Whether to skip first row on folds > 0
    @param skipNonFloatCol {Iterable<String>} Non-numeric column headers
    """
    fieldNames = None
    data = []
    if not os.path.isdir(dirName):
        print >> sys.stderr, "is not a directory, bye! %s" % dirName
    for fold in xrange(10):
        fileName = os.path.join(dirName, filePattern % fold)
        print >> sys.stderr, "Processing %s" % fileName
        if not os.path.exists(fileName):
            print >> sys.stderr, "file %s does not exist. Aborting." % fileName
            sys.exit(-1)
        fh = open(fileName, 'r')
        reader = csv.DictReader(fh, delimiter=delimiter)
        if fieldNames is not None:
            # we assume all CSV files have the same set of headers
            assert fieldNames == filter(lambda x: x != '', reader.fieldnames)
        fieldNames = reader.fieldnames
        # skip the empty string
        # we sometimes get trailing ghost columns.
        fieldNames = filter(lambda x: x != '', fieldNames)
        if skipFirstRow and fold != 0:
            skipped = reader.next()
            print >> sys.stderr, "Skipped row: %s" % skipped
        for row in reader:
            newRow = []
            data.append(newRow)
            for item in fieldNames:
                if item not in skipNonFloatCol:
                    val = float(row[item].replace(',', '.'))
                else:
                    val = row[item]
                newRow.append(val)
    avgRow = []
    # How many columns to skip for average
    # these are copied from the first row (==file)
    skipInitial = len(skipNonFloatCol)
    for column in xrange(len(fieldNames)):
        if column < skipInitial:
            avgRow.append(data[0][column])
        else:
            columnSum = 0.0
            count = 0.0
            for newRow in data:
                count += 1
                columnSum += newRow[column]
            avgRow.append(columnSum / count)
    data.append(avgRow)
    outFile = os.path.join(dirName, outFileName)
    if os.path.exists(outFile):
        os.rename(outFile, outFile + '.back')
    outFH = open(outFile, 'w')
    writer = csv.writer(outFH, delimiter=';')
    writer.writerow(fieldNames)
    for row in data:
        writer.writerow(row)
    outFH.close()


if __name__ == "__main__":
#    main(sys.argv[1], filePattern="all_%s.csv", delimiter=';',
#         skipFirstRow=False, skipNonFloatCol=frozenset([]))
    print >> sys.stderr, "Calling merge_csv_average.py directly is deprecated."
    sys.exit(-1)

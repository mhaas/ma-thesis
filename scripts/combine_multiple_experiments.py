#!/usr/bin/env python

import csv
import sys
import glob
import os

# This script combines the all.csv of several different runs.
# See merge_csv_average.py


DESIRED_LABELS = ["labelsAcc", "rootLabelsAcc",
                  "NegativelabelFScore", "NeutrallabelFScore",
                  "PositivelabelFScore",
                  "combinedLabelFMacro",
                  "combinedLabelAccMacro",
                  "NegativerootLabelFScore", "NeutralrootLabelFScore",
                  "PositiverootLabelFScore",
                  "combinedRootLabelAccMacro",
                  "NegativelabelAcc", "NeutrallabelAcc", "PositivelabelAcc",
                  "NegativerootLabelAcc", "NeutralrootLabelAcc",
                  "PositiverootLabelAcc"
                  ]


def get_row(dirName):
    """Retrieves the DESIRED_LABELS from last row in CSV file.

    The underlying assumption is that the last row in a CSV file
    is the average over all cross-validation folds in the experiment.

    Such files are produced by merge_csv_average.py and related files.

    @param dirName {string} Path to directory containing all.csv
    @returns CSV row {list<string>} Only DESIRED_LABELS field
    """
    csvFile = os.path.join(dirName, 'all.csv')
    if not os.path.exists(csvFile):
        print >> sys.stderr, "CSV File does not exist. Bailing out..."
        print >> sys.stderr, csvFile
        sys.exit(1)
    fh = open(csvFile, 'r')
    reader = csv.DictReader(fh, delimiter=";")
    lastRow = None
    for row in reader:
        print row
        lastRow = row
    row = []
    for label in DESIRED_LABELS:
        row.append(lastRow[label])
    return row


def main(rootDirName, header, detailsExtractor, dirPattern='*',
         rejectPattern=None):
    """
    This script summarizes several experiments. Each experiment consists
    of a several (typically ten) cross-validation runs. The individual
    results are stored in a file called all.csv in the subdirectory of the
    experiment.

    The detailsExtractor parameter is a function which extracts the experiment
    parameters (its name) from the file name. The header list indicates the
    name of the extracted fields.

    @param rootDirName {string} Directory containing experiment subdirectories
    @param header {list<string>} List of column names
    @param detailsExtractor {function} Extracts value list from dir name
    @param dirPattern {string} Optional restriction on evaluated dir names
    @param rejectPattern {regex pattern} Matched directory names are excluded
    """
    rows = []
    for dirName in glob.glob(os.path.join(rootDirName, dirPattern)):
        baseDirName = os.path.basename(dirName)
        if not os.path.isdir(dirName):
            print "is not a directory, skipping: %s" % dirName
            continue
        if rejectPattern and rejectPattern.match(baseDirName):
            print "rejectPattern matched %s, skipping" % baseDirName
            continue
        values = detailsExtractor(baseDirName)
        if not header or not values:
            print >> sys.stderr, ("Could not get header or values for %s"
                                  % baseDirName)
        values.extend(get_row(dirName))
        rows.append(values)
    outFH = open(os.path.join(rootDirName, 'all-combined.csv'), 'w')
    writer = csv.writer(outFH, delimiter=';')
    header.extend(DESIRED_LABELS)
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)
    outFH.close()

if __name__ == "__main__":
    main(sys.argv[1])

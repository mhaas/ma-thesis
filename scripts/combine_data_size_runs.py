#!/usr/bin/env python
# -*- coding utf-8 -*-

import glob
import os.path
import re
import csv
import sys


def fix_comma(row):
    """Fix decimal delimiter.

    The Java code outputs , instead of . depending on the locale.
    """
    res = []
    for item in row:
        if isinstance(item, basestring):
            item = item.replace(',', '.')
        res.append(item)
    return res


def main(directory):
    pattern = re.compile('all_(\d{1,4})\.csv')
    header = None
    rows = []
    for csvFile in glob.glob(os.path.join(directory, 'all_*.csv')):
        fileName = os.path.basename(csvFile)
        if fileName == 'all_combined.csv':
            continue
        match = pattern.match(fileName)
        assert match
        count = match.group(1)
        fh = open(csvFile)
        reader = csv.reader(fh, delimiter=';')
        header = reader.next()
        line = reader.next()
        line.insert(0, int(count))
        rows.append(fix_comma(line))
        fh.close()
    header.insert(0, 'numSentences')
    outFH = open(os.path.join(directory, 'all_combined.csv'), 'w')
    writer = csv.writer(outFH, delimiter=';')
    writer.writerow(header)
    writer.writerows(rows)
    outFH.close()

if __name__ == '__main__':
    main(sys.argv[1])

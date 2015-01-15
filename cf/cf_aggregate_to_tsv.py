#/usr/bin/env python
# -*- coding: utf-8 *-*

import csv
import sys


def main(inFile, outFile):
    inFH = open(inFile)
    reader = csv.DictReader(inFH)
    outFH = open(outFile, 'w')
    writer = csv.writer(outFH, delimiter='\t', quoting=csv.QUOTE_NONNUMERIC)
    for row in reader:
        segment = row['content']
        sentiment = int(row['sentiment'])
        # Manually quote segment
        # csv module does not allow "Only quote string" out of the box
        writer.writerow([segment, sentiment])
    inFH.close()
    outFH.close()

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

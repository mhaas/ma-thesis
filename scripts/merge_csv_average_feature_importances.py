#!/usr/bin/env python

import sys

# This script merges evaluation results for different splits
# and stores the output in all.csv

from merge_csv_average import main

if __name__ == '__main__':
    main(sys.argv[1], filePattern='feature_imp_%s.csv', delimiter=',',
         skipFirstRow=False,
         skipNonFloatCol=frozenset(['name']),
         outFileName='all_feature_imp.csv')

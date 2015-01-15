#!/usr/bin/env python

import sys

# This script merges evaluation results for different splits
# and stores the output in all.csv

from merge_csv_average import main


if __name__ == "__main__":
    main(sys.argv[1], filePattern="proj_%s.csv", delimiter=',',
         skipFirstRow=False, skipNonFloatCol=frozenset(["type", "run"]))

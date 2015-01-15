#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

for l in sys.stdin:
    line = l.strip().split()
    count = int(line[2])
    if count < int(sys.argv[2]):
        continue
    clust = line[0][:int(sys.argv[1])]
    print "%s\tK-%s" % (line[1], clust)

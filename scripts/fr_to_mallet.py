#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import glob


def main(inDir, outFile):
    outFH = open(outFile, "w")
    for f in glob.iglob(os.path.join(inDir, "*.split")):
        base = os.path.basename(f)
        fh = open(f, "r")
        review = " ".join(map(lambda x: x.strip(), fh.readlines()))
        outFH.write(base)
        outFH.write(" ")
        outFH.write("N/A")
        outFH.write(" ")
        outFH.write(review)
        outFH.write("\n")
        fh.close()
    outFH.close()

if __name__ == "__main__":
    import sys
    main(sys.argv[1], sys.argv[2])

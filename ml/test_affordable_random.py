#!/usr/bin/env python

import subprocess
import random

files = [500, 1000, 1500, 2000, 2500, 5000, 10000]
file_pattern = ["affordable_unuseful_10000.csv.shuffled/data_split_%s",
                "affordable_useful_10000.csv.shuffled/data_split_%s"]
boxes = ["08", "09", "11", "20", "24", "23", "25", "26", "27"]

for box in boxes:
    print "ssh pool%s" % box

for f in files:
    for p in file_pattern:
        pref = "/home/students/haas/ma/amzn/"
        full = (pref + p) % f
        box = "pool%s" % random.choice(boxes)  # boxes.pop()
        cmd = "/usr/bin/ssh %s /home/students/haas/kurse/Master-Arbeit/code/ml/test_single.sh %s" % (box, full)
        subprocess.Popen(cmd, shell=True)

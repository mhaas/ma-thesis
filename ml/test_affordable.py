#!/usr/bin/python

import subprocess
import random

#files = [2500, 5000, 10000]
#files = [500, 1000, 1500, 2000]
#file_pattern = ["affordable_useful_%s.csv", "affordable_unuseful_%s.csv"]

files = [2000]
file_pattern = ["affordable_useful_%s.csv"]
boxes = ["08", "09", "11", "20", "24", "23"]

for f in files:
    for p in file_pattern:
        pref = "/home/students/haas/ma/amzn/"
        full = (pref + p) % f
        box = "pool%s" % random.choice(boxes) #boxes.pop()
        cmd = "/usr/bin/ssh %s /home/students/haas/kurse/Master-Arbeit/code/ml/test_single.sh %s" % (box, full)
        subprocess.Popen(cmd, shell=True)

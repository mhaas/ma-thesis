#!/usr/bin/env python
# -*- coding: utf-8 -*-

import nltk.tree
import nltk.draw
import sys
import shared.ma_util


def main(treeBank):
    count = 0
    for tree in shared.ma_util.readPenn(treeBank):
        print 'Drawing tree %s' % count
        tv = nltk.draw.TreeView(tree)
        #tv.mainloop()
        tv._cframe.print_to_file('out-%s.eps' % count)
        count += 1

if __name__ == '__main__':
    main(sys.argv[1])

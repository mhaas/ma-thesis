#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import film_rezensionen as fr
import os

class FRTest(unittest.TestCase):

    baseDir = "raw"

    def readSoup(self, fileName):
        return fr.fetch_as_soup(u"some_url", os.path.join(FRTest.baseDir, fileName))

    def test1(self):
        soup = self.readSoup(u"zimmer-205-traust-du-dich-rein.html")
        w = fr._getWertung(soup)
        self.assertEqual(w, (u"Wertung: 6 von 10", 0.6))

    def test2(self):
        soup = self.readSoup(u"paranormal-vitality.html")
        w = fr._getWertung(soup)
        self.assertEqual(w, (u"Wertung: 5 von 10", 0.5))

        


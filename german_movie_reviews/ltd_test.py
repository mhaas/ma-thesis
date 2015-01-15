#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import list_tokenization_discrepancy as ftd


class Test(unittest.TestCase):

    def setUp(self):
        self.text1 = "sabata.html.txt"
        self.text1q = self.readText("tests/txt-quoted/" + self.text1)
        self.text1u = self.readText("tests/txt-without-quotes/" + self.text1)
        self.text2 = "das-biest-muss-sterben.html.txt"
        self.text2q = self.readText("tests/txt-quoted/" + self.text2)
        self.text2u = self.readText("tests/txt-without-quotes/" + self.text2)
        
        self.text3 = "same_number_of_sentences.txt"
        self.text3_1 = self.readText("tests/" + "same_number_of_sentences_1.txt")
        self.text3_2 = self.readText("tests/" + "same_number_of_sentences_2.txt")
        self.text4 = "zweitausendeins-odyssee-im-dvd-regal.html.txt"
        self.text4q = self.readText("tests/txt-quoted/" + self.text4)
        self.text4u = self.readText("tests/txt-without-quotes/" + self.text4)
        self.text4qs = self.readTokens("tests/txt-quoted-split/" + self.text4 + ".split")
       
        self.text5 = "terminator-die-erlosung.html.txt"
        self.text5t = self.readTokens("tests/txt-quoted-split/" + self.text5 + ".split")
        self.text5g = self.readText("tests/txt-without-quotes/" + self.text5)

        self.text6 = "terminator-2-tag-der-abrechnung.html.txt"
        self.text6t = self.readTokens("tests/txt-quoted-split/" + self.text6 + ".split")
        self.text6g = self.readText("tests/txt-without-quotes/" + self.text6)


        self.text7 = "gefahrliche-begegnung.html.txt"
        self.text7t = self.readTokens("tests/txt-quoted-split/" + self.text7 + ".split")
        self.text7g = self.readText("tests/txt-without-quotes/" + self.text7)


    def readText(self, fileName):
        fh = open(fileName, "r")
        text = fh.read().decode("utf-8")
        fh.close()
        return text
    
    def readTokens(self, fileName):
        fh = open(fileName, "r")
        text = [x.decode("utf-8") for x in fh.readlines()]
        fh.close()
        return text

    def test1(self):
        res = ftd.diff(self.text1q, self.text1u, self.text1, False)
        self.assertEqual(res["MERGE"], [(self.text1, 27, 28)])
        
    def test2(self):
        res = ftd.diff(self.text2q, self.text2u, self.text2, False)
        self.assertEqual(res["MERGE"], [(self.text2, 39, 40)])


    def test3(self):
        # tests whether actual differences between sentence splits are recognized
        # so we don't just check on number of sentence
        res = ftd.diff(self.text3_1, self.text3_2, self.text3, False)
        self.assertNotEqual(res["MERGE"], [])

    #@unittest.expectedFailure
    # TODO: what is going on here?
    def test4(self):
        # fails because here the gold is split unexpectedly
        res = ftd.diff(self.text4q, self.text4u, self.text4, False)
        # Does not matter, crashes...
        self.assertEqual(res["MERGE"], [])

    # Uses pre-merged gold
    def test4a(self):
        res = ftd.diff(self.text4qs, self.text4u, self.text4, True)
        # Does not matter, crashes...
        self.assertEqual(res["MERGE"], [])

    def test5(self):
        # def diff(quotedText, unquotedText, baseName, goldAlreadyTokenized):
        res = ftd.diff(self.text5t, self.text5g, self.text5, True)
        self.assertEqual(res["MERGE"], [])

    def test6(self):
        # def diff(quotedText, unquotedText, baseName, goldAlreadyTokenized):
        res = ftd.diff(self.text6t, self.text6g, self.text6, True)
        #self.assertEqual(res["MERGE"], [(self.text6, 29, 30)])
        self.assertEqual(res["MERGE"], [(self.text6, 28, 29)])

    def test7(self):
        # def diff(quotedText, unquotedText, baseName, goldAlreadyTokenized):
        res = ftd.diff(self.text7t, self.text7g, self.text7, True)
        self.assertEqual(res["MERGE"], [(self.text7, 19, 20)])

 

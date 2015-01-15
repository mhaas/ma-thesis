#!/usr/bin/python
# -*- coding: utf-8 -*-

# This script merges TigerXML alignment files.
# This is useful if you want a single representation
# of all three sub-corpora in SMULTRON 3.0.

#from lxml import etree
import xml.etree.cElementTree as etree
import sys
import os
import re


# TODO: can also be implemented by refering treebanks using
# different ids

SIDRE = re.compile(ur"s(\d+)")
NIDRE = re.compile(ur"s(\d+)_(\d+)")


def main(alignments):
    # load alignments in lxml
    masterAlignment = makeMasterAlignment()
    masterTreebanks = {}
    masterTreebanks["EN"] = makeMasterTreebank()
    masterTreebanks["DE"] = makeMasterTreebank()
    offsetDE = 0
    offsetEN = 0
    for f in alignments:
        print f
        base = os.path.dirname(f)
        fh = open(f, "r")
        tree = etree.parse(fh)
        (bankEN, bankDE) = resolveTreebanks(tree, base)
        mergeAnnotations(masterTreebanks["EN"], bankEN)
        mergeAnnotations(masterTreebanks["DE"], bankDE)
        countEN = mangleTreebank(bankEN, offsetEN)
        # make sure these use the same identifier??
        countDE = mangleTreebank(bankDE, offsetDE)
        mangleAlignment(tree, offsetEN, offsetDE)
        attachToMasterAlignment(masterAlignment, tree)
        attachToMasterTreebank(masterTreebanks["EN"], bankEN)
        attachToMasterTreebank(masterTreebanks["DE"], bankDE)
        offsetEN += countEN
        offsetDE += countDE
    etree.ElementTree(masterAlignment).write("alignment.xml")
    etree.ElementTree(masterTreebanks["EN"]).write("en.xml")
    etree.ElementTree(masterTreebanks["DE"]).write("de.xml")


def attachToMasterAlignment(masterAlignment, tree):
    master = masterAlignment.find(".//alignments")
    alignments = tree.find(".//alignments")
    for alignment in alignments:
        master.append(alignment)


def attachToMasterTreebank(masterTreebank, tree):
    master = masterTreebank.find(".//body")
    sentences = tree.find(".//body")
    for sentence in sentences:
        master.append(sentence)


def makeMasterAlignment():
    s = """<treealign subversion="3" version="2">
  <head>
    <alignment-metadata>
      <author>--</author>
      <date>2009-05-13</date>
      <description></description>
      <history>
        <change date="2009-05-13" author="Martin Volk">save operation</change>
      </history>
      <license>Creative Commons Attribution-Noncommercial 2.5 Switzerland</license>
      <revision>48</revision>
      <size>11278</size>
      <uuid>4373c194-8e01-48e6-8b8d-6c9a6572f126</uuid>
    </alignment-metadata>
    <treebanks>
      <treebank id="de" language="de_DE" filename="de.xml"/>
      <treebank id="en" language="en_US" filename="en.xml"/>
    </treebanks>
    <settings>
      <display-options>
        <top-treebank treebank-id=""/>
      </display-options>
      <auto-align active="False"/>
    </settings>
  </head>
    <alignments></alignments></treealign>"""
    tree = etree.fromstring(s)
    return tree


def makeMasterTreebank():
    # create dummy treebank
    s = """<corpus xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.cl.uzh.ch/kitt/treealigner/data/schema/TigerXML.xsd" id="SMULTRON_DE_Alpine">
  <head>
    <meta>
      <name>SMULTRON_DE_Alpine</name>
      <author>Annette Rios</author>
      <date>2010-12-23</date>
      <description>Part of SMULTRON v3.0 – The Stockholm MULtilingual parallel TReebank. See http://www.cl.uzh.ch/research/paralleltreebanks/smultron_en.html</description>
      <format>German TIGER Format</format>
    </meta>
    <annotation></annotation></head><body></body></corpus>"""
    tree = etree.fromstring(s)
    return tree


def resolveTreebanks(tree, base):
    # obtain links to treebanks
    """<treebank id="DE" language="de_DE" filename="treebanks/de/smultron_de_dvdman.xml"/>
      <treebank id="EN" language="en_US" filename="treebanks/en/smultron_en_dvdman.xml"/>"""
    bankDE = tree.find(".//treebank[@language='de_DE']").get("filename")
    bankEN = tree.find(".//treebank[@language='en_US']").get("filename")
    bankDE = etree.parse(open(os.path.join(base, bankDE)))
    bankEN = etree.parse(open(os.path.join(base, bankEN)))
    return (bankEN, bankDE)


def mangleTreebank(treebank, offset):
    name = treebank.find(".//meta/name").text
    name = name.lower()
    body = treebank.find(".//body")
    count = 0
    for foo in ["id", "root", "idref"]:
        for elem in body.iterfind(".//*[@%s]" % foo):
            count += 1
            i = elem.get(foo)
            print i
            print elem.tag
            match = NIDRE.match(i)
            if match is None:
                match = SIDRE.match(i)
                sentenceIdx = match.group(1)
                elem.set(foo, "s%s" % (int(sentenceIdx) + offset))
            else:
                sentenceIdx = match.group(1)
                tokenIdx = match.group(2)
                elem.set(foo, "s%s_%s" % (int(sentenceIdx) + offset, tokenIdx))
    return count


def mangleAlignment(tree, offsetEN, offsetDE):
    alignments = tree.find(".//alignments")
    for foo in ["node_id"]:  # , "root-id"]:
        for elem in alignments.iterfind(".//*[@%s]" % foo):
            # this is not proper, but it works
            lang = elem.get("treebank_id")
            print "Lang is %s" % lang
            i = elem.get(foo)
            match = NIDRE.match(i)
            sentenceIdx = match.group(1)
            tokenIdx = match.group(2)
            if lang.lower() == "de":
                offset = offsetDE
            elif lang.lower() == "en":
                offset = offsetEN
            else:
                print elem
                assert False
            elem.set(foo, "s%s_%s" % (int(sentenceIdx) + offset, tokenIdx))


def mergeAnnotations(master, tree):
    masterA = master.find(".//annotation")
    for feature in tree.find(".//annotation"):
        # we can have       <feature name="cat" domain="NT">
        # and <edgelabel>, <secedgelabel>,
        tag = feature.tag
        if tag == "feature":
            featureName = feature.get("name")
            masterFeature = masterA.find("feature[@name='%s']" % featureName)
        else:
            masterFeature = masterA.find(tag)

        if not masterFeature:
            masterA.append(feature)
        else:
            # feature exists, now copy all values
            for value in feature:
                valueName = value.get("name")
                print valueName
                if not masterFeature.find('value[@name="%s"]' % valueName):
                    masterFeature.append(value)


if __name__ == "__main__":
    main(sys.argv[1:])

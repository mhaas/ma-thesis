#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import nltk
import nltk_contrib.tiger
from lxml import etree
import itertools
from indexer import SimpleIndexer
import logging
import ma_util
import deprecated
import tigerhelper as th
from tigerhelper import TigerHelper

print nltk.__version__

logger = logging.getLogger("project")

# how many sentiment labels we projected
countMappingApplied = 0
# how many times we had a sentiment label in the source,
# but no alignment link for that node
countSourceNotInAlignment = 0
# how many times we had an alignment,
# but could not find the target node in the target tree
countTargetNotFound = 0


@deprecated.deprecated
def walkTree(tree):
    return ma_util.walkTree(tree)


@deprecated.deprecated
def readPenn(treeBank):
    return ma_util.readPenn(treeBank)


def readTiger(treeBank):
    """Reads parse trees from TigerXML files.
    @param treeBank {basestring} File name of treebank
    @yields {TigerGraph} Parse trees
    """
    corpus = nltk_contrib.tiger.tigerxml.TigerParser()
    indexer = SimpleIndexer()
    corpus.parse(treeBank, indexer)
    for sentence in indexer.g:
        yield sentence


def readAlignment(alignmentFile, types=None):
    """Reads alignment from alignmentFile.

    Alignment must be stored in Stockholm Treealigner XML format.
    The types parameter can restrict the alignment types included.
    Typically, it will be a list containing "good", "fuzzy"
    or both. If the parameter is None, all alignments will be returned.

    Alignment direction is swapped. If the alignment file contains
    a link:
        <node node_id="s0_23" type="t" treebank_id="1"/>
        <node node_id="1_52" type="t" treebank_id="2"/>
    then the resulting mapping will contain { "1_52" : "s0_23" }.


    @param alignmentFile {basestring} Alignment file
    @param types {list{basestring}} Alignment types
    @returns {dict} Mapping from source to target nodes
    """
    res = {}
    fh = open(alignmentFile, "r")
    document = etree.parse(fh)
    treebanks = document.find(".//treebanks")
    source = treebanks[0].get("filename")
    target = treebanks[1].get("filename")
    typeCount = {}

    for align in document.iterfind(".//align"):
        alignType = align.get("type")
        if types is not None:
            if not alignType in types:
                continue
            if not alignType in typeCount:
                typeCount[alignType] = 0
            typeCount[alignType] += 1
        sourceTreebank = align[0].get("treebank_id")
        assert sourceTreebank == "1"
        sourceID = align[0].get("node_id")
        targetID = align[1].get("node_id")
        targetTreebank = align[1].get("treebank_id")
        assert targetTreebank == "2"
        # we swap these
        res[targetID] = sourceID
        #<node node_id="s0_23" type="t" treebank_id="1"/>
        #<node node_id="1_52" type="t" treebank_id="2"/>
    print "Alignment links per type: %s" % typeCount
    fh.close()
    return {"source": source, "target": target, "alignment": res}


def _tigerToTreeRec(tigerGraph, tigerNodeID, treeNode):
    nextTigerNodeID = tigerNodeID
    tigerNode = tigerGraph.nodes[nextTigerNodeID]
    if isinstance(tigerNode, nltk_contrib.tiger.graph.TerminalNode):
        return
    for edge in tigerNode:
        tigerChildID = edge[1]
        childNode = tigerGraph.nodes[tigerChildID]
        if isinstance(childNode, tuple):
            childTreeNode = nltk.tree.Tree(childNode[1], [])
            treeNode.append(childTreeNode)
        else:
            childTreeNode = nltk.tree.Tree(childNode.id, [])
            treeNode.append(childTreeNode)
            _tigerToTreeRec(tigerGraph, tigerChildID, childTreeNode)


def tigerToTree(tiger):
    """Converts TigerGraph instance to nltk.tree.Tree.

    Node labels will be node IDs from the TigerGraph instance.
    All other information is discarded.

    @param tiger {TigerGraph} Tree to be converted
    @returns {nltk.trees.Tree} Converted tree with node IDs as labels
    """
    if isinstance(tiger, basestring):
        graph = readTiger(tiger).next()
    else:
        graph = tiger
    # We used to use the sentence ID for the root node,
    # but ID of the root node is a better fit
    tree = nltk.tree.Tree(graph.root_id, [])
    _tigerToTreeRec(graph, graph.root_id, tree)
    return tree


def getMappingFromNodeIDToSentiment(tigerSentence, pennSentence):
    """Extracts sentiment values for node IDs.

        Given a parse tree in TigerXML format and a sentiment-annotated
        parse tree in Penn Treebank format, this methods extracts
        the sentiment values for each node and matches it
        to the node ID obtained from the TigerXML file.

        Both trees must be isomorphic.

        @param tigerSentence TigerGraph object containing a sentence parse tree
        @param pennSentence NLTK Tree containing a sentence parse tree
        @returns Mapping from node IDs to sentiment values
      """

    res = {}
    for (tigerNode, pennNode) in itertools.izip_longest(
            ma_util.walkTree(tigerToTree(tigerSentence)), ma_util.walkTree(pennSentence),
            fillvalue="LIST_LENGTH_NOT_EQUAL"):
        tigerID = tigerNode.node
        pennSentiment = pennNode.node
        res[tigerID] = pennSentiment
    return res


def applyMappingToTarget(mapping, alignment, tigerHelper, stripTargetIDPrefix):
    """Applies sentiment values to target.

       Given a mapping from source node IDs to sentiment values
        and an alignment between source and target node IDs,
       the sentiment values are applied to the target tree.

       @param mapping map from source node IDs to sentiment values
       @param alignment map from source node IDs to target node IDs
       @param target etree parse tree - will be modified
    """
    global countSourceNotInAlignment
    global countMappingApplied
    global countTargetNotFound
    for (sourceID, sentiment) in mapping.iteritems():
        if not sourceID in alignment:
            logger.warn("Source node ID %s not found in alignment.", sourceID)
            countSourceNotInAlignment += 1
            continue
        targetID = alignment[sourceID]
        origTargetID = targetID
        if stripTargetIDPrefix:
            targetID = ma_util.stripPrefixFromString(targetID)
        node = tigerHelper.getNode(targetID)
        if node is None:
            logger.warn("Could not find target node with ID %s", targetID)
            countTargetNotFound += 1
            continue
        if node.tag == "s":
            continue
        countMappingApplied += 1
        th.setSentiment(node, sentiment, th.SEN_MAPPED)
        node.set("x-source-id", sourceID)
        node.set("x-original-id", origTargetID)


def main(inputFile, annotations, alignment, targetFile, output,
         stripTargetIDPrefix, applyParentSentiment, projectRootSentiment,
         alignTypes):
    """
    Projects sentiment labels from a source tree to a target tree
    using an alignment between source and target nodes.

    @param inputFile {basestring} Filename of source treebank in TigerXML
           format
    @param annotations {basestring} Filename of treebank with sentiment labels
           in Penn Treebank format
    @param alignment {basestring} Filename of mapping between source and
           target nodes in Stockholm Treealigner format
    @param targetFile {basestring} Filename of target treebank in TigerXML
           format
    @param output {basestring} Filename for resulting output file
    @param stripTargetIDPrefix {boolean} Whether to strip alphabetic prefixes
           from node IDs in target tree
    @param applyParentSentiment {boolean} Whether to infer sentiment labels
          for unaligned nodes from ancestor nodes
    @param projectRootSentiment {boolean} Whether to perform implicit alignment
    between source and target root nodes if unaligned
    @param alignTypes {list} Which link types to include: good, fuzzy or both
    """
    mapping = {}
    logger.info("Loading alignment.")
    alignment = readAlignment(alignment, alignTypes)
    logger.info("Done loading alignment.")
    logger.info("Alignment source was: %s", alignment["source"])
    logger.info("Alignment target was: %s", alignment["target"])
    alignment = alignment["alignment"]
    logger.info("Collapsing unary nodes for source file")
    # Now get some node statistic from source/input side
    # This means we have to load the file again in tigerHelper
    inputHelper = TigerHelper(inputFile)
    print ("Target has %s nodes (T, NT) before unary-collapsing nodes"
           % inputHelper.count)
    del inputHelper
    # Now overwrite inputFile variable!
    inputFile = th.collapseToTmp(inputFile, alignment.keys())
    logger.info("Wrote unary-collapsed source tigerXML to %s", inputFile)
    logger.info("Extracting mapping from source ID to sentiment value.")
    for (tigerSentence, pennSentence) in itertools.izip_longest(
            readTiger(inputFile), ma_util.readPenn(annotations),
            fillvalue="LIST_LENGTH_NOT_EQUAL"):
        mapping.update(
            getMappingFromNodeIDToSentiment(tigerSentence, pennSentence))
    logger.info("Done extracting mapping.")
    fh = open(targetFile, "r")
    target = etree.parse(fh)
    fh.close()
    tigerHelper = TigerHelper(target, stripTargetIDPrefix)
    print "Target has %s nodes (T, NT)" % tigerHelper.count
    logger.info("Applying mapping to target.")
    applyMappingToTarget(
        mapping, alignment, tigerHelper, stripTargetIDPrefix)
    print ("Source nodes with sentiment, not in alignment: %s"
           % countSourceNotInAlignment)
    print ("Nodes with sentiment and alignment, but not found "
           + "in target tree: %s" % countTargetNotFound)
    print ("Sentiment label projected using alignment for %s nodes"
           % countMappingApplied)
    logger.info("Done applying mapping.")
    logger.info("Unary-collapsing nodes in target tree.")
    tigerHelper.collapseUnary()
    logger.info("Done collapsing unary nodes.")
    print ("After collapsing unary nodes, Target has %s nodes (T, NT)"
           % tigerHelper.count)
    logger.info("Fixing up remaining nodes")
    # Need to map root sentiment before looking up parent sentiment
    # so we can use the new information
    if projectRootSentiment:
        logger.info("Projecting root sentiment for unaligned root nodes.")
        mapRootSentiment(ma_util.readPenn(annotations), tigerHelper)
        logger.info("Done projecting root sentiment.")
    if applyParentSentiment:
        logger.info("Using parent lookup for nodes with"
                    + "unknown sentiment values.")
        (modTree, count) = tigerHelper.applyParentSentimentValue()
        print "Applied parent sentiment value for %s nodes" % count
    else:
        logger.info("Using default for nodes with unknown sentiment values.")
        (modTree, count) = tigerHelper.applyDefaultSentimentValue()
        print "Applied default sentiment value for %s nodes" % count
    logger.info("Done fixing up remaining nodes.")
    logger.info("Saving to disk...")
    tigerHelper.tree.write(output)
    logger.info("Done!")


def mapRootSentiment(source, tigerHelper, force=False):
    """Maps top-level sentiment between source and target sentences.

    If the target root node is not aligned and only has the default
    sentiment, we apply the sentiment value of the source root node
    to the target root node. We assume that root nodes always are implicitly
    aligned.

    The optional force parameter specifies whether the root sentiment
    is always mapped. This will override any previous mapping based on
    node alignments.

    @param source {Iterable{nltk.trees.Tree}} Source PTB trees
    @param target {etree} Target TigerXML tree, will be modified
    @param force {boolean} If True, always map sentiment between root nodes
    @returns Modified TigerXML tree
    """
    for (sourceSentence, targetSentence) in itertools.izip_longest(
            source,
            th.getSentences(tigerHelper.tree),
            fillvalue="LIST_LENGTH_NOT_EQUAL"):
        rootNode = tigerHelper.getSentenceRoot(targetSentence)
        metaS = rootNode.get("x-sentiment")
        # we will typically get here before default sentiment values
        # have been applied, so metaS might be None.
        #assert metaS is not None
        if (not force and metaS == th.SEN_MAPPED):
            continue
        else:
            logger.debug("Mapping root sentiment %s for target %s",
                         sourceSentence.node, th.getNodeID(rootNode))
            th.setSentiment(rootNode, sourceSentence.node, th.SEN_MAPPED_ROOT)

if __name__ == "__main__":
    logging.basicConfig(filename='project.log', level=logging.INFO,
                        format='%(asctime)s:%(module)s:'
                        + '%(levelname)s:%(message)s')

    parser = argparse.ArgumentParser(
        description='Apply sentiment annotation given a treebank alignment.')
    parser.add_argument('--input', required=True,
                        help='Input treebank.')
    parser.add_argument('--annotations', required=True,
                        help='Sentiment annotation in PTB format')
    parser.add_argument('--alignment', required=True,
                        help='Alignment file for input and target')
    parser.add_argument('--target', required=True,
                        help='Treebank to which the sentiment annotation '
                        + 'will be projected')
    parser.add_argument('--output', required=True,
                        help='Output file')
    parser.add_argument('--strip-target-id-prefix', required=False,
                        action="store_true",
                        help='Strip alphabetic prefix from node IDs')
    parser.add_argument('--apply-parent-sentiment', required=False,
                        action="store_true",
                        help='Infer sentiment value from parents for '
                        + 'unknown nodes. Otherwise, apply a default value.')
    parser.add_argument('--map-root-sentiment', required=False,
                        action="store_true",
                        help='Infer sentiment values for root nodes from '
                        + 'source root node. Performs implicit alignment '
                        + 'between root nodes.')
    parser.add_argument('--alignment-types', required=False,
                        choices=['good', 'fuzzy'],
                        action="append",
                        default=['good', 'fuzzy'],
                        help="Specify which alignment links will be included.")

    args = parser.parse_args()
    logger.info("Started with args: %s", args)
    main(args.input, args.annotations,
         args.alignment, args.target, args.output, args.strip_target_id_prefix,
         args.apply_parent_sentiment, args.map_root_sentiment,
         args.alignment_types)

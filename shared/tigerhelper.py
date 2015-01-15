
# -*- coding: utf-8 -*-

import logging
from lxml import etree
from collections import OrderedDict
import tempfile
import ma_util

logger = logging.getLogger("tigerhelper")

SEN_MAPPED = "MAPPED"
SEN_DEFAULT = "DEFAULT"
SEN_MAPPED_ROOT = "MAPPED_ROOT"
SEN_ANCESTOR = "ANCESTOR"


class TigerHelper(object):

    def __init__(self, tiger, stripPrefixFromID=False):
        if isinstance(tiger, basestring):
            fh = open(tiger)
            self.tree = etree.parse(fh)
            fh.close()
        elif isinstance(tiger, file):
            self.tree = etree.parse(tiger)
        else:
            self.tree = tiger
        if stripPrefixFromID is True:
            self.stripPrefixFromID()
        self._buildCache()

    def _buildCache(self):
        (self.cache, self.edges, self.count) = buildNodeIDCache(self.tree,
                                                                True)

    def getChildren(self, node):
        """Returns child nodes of a node.

            @param node {basestring or etree} Parent node
            @param sentenceFragment {etree} XML sentence fragment
            @returns {list{etree}} List of child nodes
        """
        e = self.edges.get(node)
        if e is None:
            return []
        else:
            return map(lambda nodeID: self.getNode(nodeID), e)

    def setChildren(self, node, children):
        # remove edges
        self.edges[node] = []
        for child in node.getchildren():
            node.remove(child)
        for newChild in children:
            if isinstance(newChild, basestring):
                childNodeID = newChild
            elif isinstance(newChild, etree._Element):
                if newChild.tag == "edge":
                    childNodeID = newChild.get("idref")
                else:
                    childNodeID = newChild.get("id")
            else:
                raise ValueError("Unknown argument %s!" % newChild)
            etree.SubElement(node, "edge", {"idref": childNodeID,
                                            "label": "--"})
            self.edges[node].append(childNodeID)

    def getNode(self, nodeID):
        """Looks up a node given its ID in a sentence fragment.

        @param nodeID {basestring} ID of a node
        @returns {etree} Node
        """
        node = self.cache.get(nodeID)
        return node

    def applyDefaultSentimentValue(self, default="2"):
        """Applies default sentiment value where no label exists.

        For nodes where sentiment is set (indicated by the
        x-sentiment XML attribute), a default value is set.
        The default value typically is '2', i.e. 'neutral'.

        The return value is a tuple containing the modified
        tree and the number of modified tokens.

        @param default {basestr} default label to apply
        @returns {(etree,integer)} Tuple of modified tree and modifiedCount
        """
        modifiedCount = 0
        for node in self.cache.values():
            if node.get("x-sentiment"):
                continue
            if node.tag == "s":
                continue
            modifiedCount += 1
            setSentiment(node, default, SEN_DEFAULT)
        return (self.tree, modifiedCount)

    def getSentenceRoot(self, sentenceFragment):
        """Returns root node for a sentence fragment.

        @params sentenceFragment {etree} XML sentence fragment
        @returns {etree} root node
        """
        rootNodeID = getSentenceRootID(sentenceFragment)
        return self.getNode(rootNodeID)

    def preOrder(self, sentenceFragment, returnNodes=False,
                 forceSentiment=False):
        """Traverses a sentence in pre-order.

        Note that this will not traverse the XML tree
        in tree-order. Instead, it will traverse the encoded
        parse tree.

        @param sentenceFragment {etree} XML sentence fragment
        @param returnNodes {bool} if true, return etree XML nodes
        @param forceSentiment {bool} if true, return sentiment value even if no
                                     sentiment meta is set
        @yields Triple (node ID, node sentiment, node sentiment meta)
        """
        assert sentenceFragment is not None
        queue = []
        rootNode = self.getSentenceRoot(sentenceFragment)
        if rootNode is None:
            logger.error("Trying to traverse parse tree,"
                         + "but the root node ID is invalid.")
            assert False
        queue.append(rootNode)
        while len(queue) > 0:
            curNode = queue.pop(0)
            if returnNodes:
                yield curNode
            else:
                yield (curNode.get("id"),
                       getSentiment(curNode, forceSentiment),
                       curNode.get("x-sentiment"),
                       curNode.get("x-source-id"),
                       curNode.get("x-original-id"))
            for child in reversed(self.getChildren(curNode)):
                if child is None:
                    logger.error("Child node is None. Bailing out.")
                    assert False
                queue.insert(0, child)

    def getSentenceLeaves(self, sentenceFragment):
        leaves = []
        for node in self.preOrder(sentenceFragment, returnNodes=True):
            if not self.getChildren(node):
                leaves.append(node)
        return leaves

    def applyParentSentimentValue(self, default="2",
                                  overrideDefaults=False):
        """Applies the parent sentiment value for nodes with unknown sentiment.

        If no parent node with a valid sentiment value can be found,
        the default value is applied.
        A tuple containing the modified treebank and the count
        of modified nodes is returned.

        @param tigerXML {etree} Treebank as XML tree
        @param default {str} Default value if no valid parent is found
        @param overrideDefaults {bool} Apply sentiment even if default
                sentiment was set beforehand
        @returns {(etree, integer)} modified treebank and modifiedCount
        """
        modifiedCount = 0
        for sentenceFragment in getSentences(self.tree):
            for node in self.preOrder(sentenceFragment, returnNodes=True):
                metaSentiment = node.get("x-sentiment")
                if metaSentiment and not (overrideDefaults
                                          and metaSentiment == SEN_DEFAULT):
                    continue
                modifiedCount += 1
                nodeID = node.get("id")
                if nodeID is None:
                    print "NodeID is none, this is.. unfortunate."
                sentiment = getParentSentiment(nodeID, sentenceFragment)
                if sentiment is None:
                    setSentiment(node, default, SEN_DEFAULT)
                else:
                    setSentiment(node, sentiment, SEN_ANCESTOR)
        return (self.tree, modifiedCount)

    def getSentence(self, sentenceID):
        """Returns sentence fragment from tree.

        @param sentenceID {basestring} Sentence ID
        @returns {etree} a sentence fragment
        """
        return self.cache.get(sentenceID)

    def collapseUnary(self, collapseConsecutive=True):
        # TODO: if we lose information due to merging nodes,
        # we might want to propagate labels up to the parent node
        # or to the child node!
        # this probably only applies if for the NT->T case
        # TODO: are leaves (almost) always neutral?
        countDeletedDefault = 0
        countDeletedMapped = 0
        for sentence in getSentences(self.tree):
            (de, ma) = self._collapseUnarySentence(sentence,
                                                   collapseConsecutive)
            countDeletedDefault += de
            countDeletedMapped += ma
        logger.info("Deleted nodes with non-default sentiment label: %s",
                    countDeletedMapped)
        logger.info("Deleted nodes with default sentiment label: %s",
                    countDeletedDefault)
        msg = ("collapseUnary: Deleted nodes with non-default "
               + "sentiment label: %s")
        print msg % countDeletedMapped
        msg = "collapseUnary: Deleted nodes with default sentiment label: %s"
        print msg % countDeletedDefault
        logger.info("Finished running collapseUnary, rebuilding node cache")
        self._buildCache()

    def collapseUnaryExcept(self, keepList, collapseConsecutive=True):
        keepList = set(keepList)
        for sentence in getSentences(self.tree):
            self._collapseUnarySentenceExcept(
                sentence, keepList, collapseConsecutive)
        logger.info("Finished running collapseUnaryExcept,"
                    + "rebuilding node cache")
        self._buildCache()

    def _collapseUnarySentenceExcept(self, sentenceFragment, keepList,
                                     collapseConsecutive):
        # premature optimization
        # but this is potentially very slow for large keepLists
        nodesInPreorder = []
        for node in self.preOrder(sentenceFragment, returnNodes=True):
            nodesInPreorder.append(node)
        for node in nodesInPreorder:
            # terminal nodes have no children
            if node.tag == "t":
                continue
            if len(node) == 0:
                continue
            elif len(node) == 1:
                nodeID = getNodeID(node)
                childNode = self.getChildren(node)[0]
                childNodeID = getNodeID(childNode)
                # we keep the parent if it is in keeplist
                # else, we keep the child (i.e. we prefer the child
                # over the parent even if it is not in the keepList
                # we also prefer the child if parent and child are in the
                # keeplist
                if (nodeID in keepList
                        and not childNodeID in keepList
                        and not childNode.tag == "t"):
                    deleted = self._collapseNodeRetainParent(
                        node, sentenceFragment)
                    if collapseConsecutive:
                        # iterate
                        nodesInPreorder.insert(0, node)
                else:
                    deleted = self._collapseNodeRetainChild(
                        node, sentenceFragment)
                    if collapseConsecutive:
                        # iterate
                        nodesInPreorder.insert(0, childNode)
                nodesInPreorder.remove(deleted)

    def _collapseUnarySentence(self, sentenceFragment, collapseConsecutive):
        # How many nodes we deleted which had a sentiment value mapped
        # other than from DEFAULT
        countDeletedMapped = 0
        countDeletedDefault = 0
        nodesInPreorder = []
        for node in self.preOrder(sentenceFragment, returnNodes=True):
            nodesInPreorder.append(node)
        for node in nodesInPreorder:
            # terminal nodes have no children
            if node.tag == "t":
                continue
            if len(node) == 0:
                continue
            elif len(node) == 1:
                sMeta = node.get("x-sentiment")
                childNode = self.getChildren(node)[0]
                childTag = childNode.tag
                if (sMeta is None or sMeta == SEN_DEFAULT) or childTag == "t":
                    deleted = self._collapseNodeRetainChild(
                        node, sentenceFragment)
                    if collapseConsecutive:
                        # iterate
                        nodesInPreorder.insert(0, childNode)
                else:
                    deleted = self._collapseNodeRetainParent(
                        node, sentenceFragment)
                    if collapseConsecutive:
                        # iterate
                        nodesInPreorder.insert(0, node)
                delMeta = deleted.get("x-sentiment")
                if delMeta != SEN_DEFAULT and delMeta is not None:
                    countDeletedMapped += 1
                else:
                    countDeletedDefault += 1
                nodesInPreorder.remove(deleted)
            elif len(node) > 2:
                raise ValueError("Tree not binary.")
        return (countDeletedDefault, countDeletedMapped)
    # TODO: can we ever collapse terminal nodes?

    def _collapseNodeRetainParent(self, node, sentenceFragment):
        """Collapses unary node.

        For a tree fragment A->B->C and if A is passed to this function,
        the resulting tree will be A->C.
        All children of B will added as children
        of A.

        @param node {lxml.etree} T or NT node.
        @param sentenceFragment {lxml.etree.Element} Sentence fragment
        @returns {lxml.etree.Element} Deleted node
        """
        #logger.debug("collapseNodeRetainParent called")
        #assert len(node) == 1
        child = self.getChildren(node)[0]
        childChildren = self.getChildren(child)
        self.setChildren(node, childChildren)
        parent = child.getparent()
        if parent is None:
            logger.error("parent is none for node %s", etree.tostring(child))
        parent.remove(child)
        return child

    def _collapseNodeRetainChild(self, node, sentenceFragment):
        """Collapses unary node.

        For a tree fragment XY->A->B and if A is passed to this function,
        the resulting tree will be XY->B.
        A will be deleted from the tree.
        Other children of XY will be retained.

        @param node {lxml.etree} T or NT node.
        @param sentenceFragment {lxml.etree.Element} Sentence fragment
        @returns {lxml.etree.Element} Deleted node
        """
        #logger.debug("collapseNodeRetainChild called")
        #assert len(node) == 1
        nodeID = getNodeID(node)
        child = self.getChildren(node)[0]
        parentNode = getParent(nodeID, sentenceFragment)
        if parentNode is None:
            # this better be the graph root then
            rootNode = self.getSentenceRoot(sentenceFragment)
            assert rootNode == node
            setSentenceRoot(child, sentenceFragment)
            # get XML parent
            xmlParent = node.getparent()
            if xmlParent is None:
                logger.error("XML Parent of node is None: %s",
                             etree.tostring(node))
            node.getparent().remove(node)
            return node
        parentChildren = self.getChildren(parentNode)
        for parentChild in parentChildren:
            if parentChild.get("id") == nodeID:
                # preserve original order
                index = parentChildren.index(parentChild)
                parentChildren.remove(parentChild)
                parentChildren.insert(index, child)
        self.setChildren(parentNode, parentChildren)
        node.getparent().remove(node)
        return node

    def getSentenceSentiment(self, sentenceFragment, forceSentiment=False):
        """Returns sentiment value for a given sentence fragment.

        The root sentiment value of a sentence is determined by
        the sentiment value of its root node.

        @param forceSentiment {bool} if true, return sentiment value even if no
                                     sentiment meta is set
        """
        rootNode = self.getSentenceRoot(sentenceFragment)
        sentiment = getSentiment(rootNode, forceSentiment)
        return sentiment

    def stripPrefixFromID(self):
        """Removes alphabetic prefix from ID attributes in TigerXML tree.

        @param tree {etree} TigerXML tree
        """
        logger.info("Stripping prefixes from node IDs")
        expression = ".//*[@id]"
        nodes = self.tree.iterfind(expression)
        for node in nodes:
            nodeID = node.get("id")
            node.set("id", ma_util.stripPrefixFromString(nodeID))
        expression = ".//graph[@root]"
        nodes = self.tree.iterfind(expression)
        for node in nodes:
            nodeID = node.get("root")
            node.set("root", ma_util.stripPrefixFromString(nodeID))
        expression = ".//edge[@idref]"
        nodes = self.tree.iterfind(expression)
        for node in nodes:
            nodeID = node.get("idref")
            node.set("idref", ma_util.stripPrefixFromString(nodeID))


def getNodeID(node):
    return node.get("id")


def getSentiment(node, forceSentiment=False):
    """Returns sentiment value for a given node ID in a sentence.

    @param nodeID {str} The node ID
    @param sentenceFragment {etree} XML sentence fragment
    @param forceSentiment {bool} if true, return sentiment value even if no
                                 sentiment meta is set
    @returns {str} Sentiment value or None
    """
    s = node.get("x-sentiment")
    if not s and forceSentiment is False:
        return None
    if node.tag == "t":
        return node.get("pos")
    elif node.tag == "nt":
        return node.get("cat")
    else:
        raise ValueError("Node is neither terminal nor non-terminal.")


def setSentiment(node, sentimentValue, sentimentSource):
    """Sets the sentiment value on a node.

    @param node {etree} Node whose sentiment value is to be set
    @param sentimentValue {int} Numeric sentiment value,  [-2,2]
    @param sentimentSource {basestring} Source of sentiment annotation
    """
    node.set("x-sentiment", sentimentSource)
    if node.tag == "t":
        node.set("pos", sentimentValue)
    elif node.tag == "nt":
        node.set("cat", sentimentValue)
    else:
        raise ValueError("Unknown node type? %s", node.tag)


def buildNodeIDCache(target, includeEdges=False):
    cache = {}
    edges = {}
    count = 0
    countTNT = 0
    for node in target.iter():
        tag = node.tag
        if tag == "nt" or tag == "t" or tag == "s":
            nodeID = node.get("id")
            cache[nodeID] = node
            count += 1
            if tag != "s":
                countTNT += 1
        elif tag == "edge" and includeEdges:
            source = node.getparent()
            target = node.get("idref")
            if not source in edges:
                edges[source] = []
            edges[source].append(target)
    logger.info("Cached %s node IDs.", count)
    if includeEdges:
        return (cache, edges, countTNT)
    else:
        return cache


def getParentSentiment(nodeID, sentenceFragment):
    """Returns sentiment of parent node.

    @param nodeID {str} The node ID whose parent is inspected
    @param sentenceFragment {etree} XML sentence fragment
    @returns {str} Sentiment value or None
    """
    ancestors = getAncestors(nodeID, sentenceFragment)
    if not ancestors:
        return None
    for ancestor in ancestors:
        sentiment = getSentiment(ancestor)
        if sentiment:
            return sentiment
    return None


def getParent(nodeID, sentenceFragment):
    """Returns parent node of a node.

    @param nodeID {str} The node ID whose parent is returned.
    @param sentenceFragment {etree} XML sentence fragment
    @returns {etree} Parent node.
    """
    assert sentenceFragment.tag == 's'
    edges = sentenceFragment.xpath(".//edge[@idref='%s']" % nodeID)
    if not edges:
        return None
    assert len(edges) == 1
    edge = edges[0]
    # get source of edge
    return edge.getparent()


def getAncestors(nodeID, sentenceFragment):
    """Returns list of parents of a node in a sentence.

    @param nodeID {str} The node ID whose parents are listed
    @param  sentenceFragment {etree} XML sentence fragment
    @returns {list{etree}} List of parent nodes
    """
    res = []
    while True:
        parent = getParent(nodeID, sentenceFragment)
        if parent is None:
            break
        else:
            nodeID = parent.get("id")
            res.append(parent)
    return res


def getSentenceRootID(sentenceFragment):
    """Returns root node ID for a sentence fragment.

    @params sentenceFragment {etree} XML sentence fragment
    @returns {etree} root node
    """
    graphNode = sentenceFragment.find(".//graph")
    rootNodeID = graphNode.get("root")
    return rootNodeID


def setSentenceRoot(node, sentenceFragment):
    graphNode = sentenceFragment.find(".//graph")
    if not isinstance(node, basestring):
        node = getNodeID(node)
    graphNode.set("root", node)


def readTreebankMap(fileName, normalizer=None):
    """Returns a map from sentence ID to sentence string.
    The function specified by the normalizer parameter
    is called for each full sentence. It is expected to
    return a sanitized version of the sentence.

    This method returns an OrderedDict. The order of
    entries corresponds to sentence order in the TigerXML
    file.

    @param fileName {basestring} File name of TigerXML file
    @param normalize {function} A sanitizer method, can be None
    """
    res = OrderedDict()
    fh = open(fileName)
    treebank = etree.parse(fh)
    fh.close()
    sentences = treebank.iterfind(".//s")
    for sentence in sentences:
        sid = getNodeID(sentence)
        full = ""
        for node in sentence.iterfind(".//t"):
            full += node.get("word")
            full += " "
        if normalizer:
            full = normalizer(full)
        res[sid] = full
    return res


def getSentences(tree):
    """Returns all sentence fragments in tree.

    @param tree {etree} TigerXML
    @yields {etree} sentence fragments
    """
    nodes = tree.iterfind(".//s")
    for node in nodes:
        yield node


def constructTigerXML(sentenceList):
    """Constructs a valid TigerXML tree from a list of sentence fragments.

    @sentenceList {list{etree}} List of sentence fragments
    """
    doc = '<corpus id="constructed">'
    doc += '<head></head>'
    doc += '<body>'
    doc += '</body>'
    doc += '</corpus>'
    tree = etree.XML(doc)
    body = tree.find(".//body")
    for sentence in sentenceList:
        body.append(sentence)
    return tree


def collapseToTmp(inputFile, skipList=[]):
    th = TigerHelper(inputFile)
    th.collapseUnaryExcept(skipList)
    tempFH = tempfile.NamedTemporaryFile(delete=False)
    tempFH.write(etree.tostring(th.tree).encode("utf-8"))
    tempFH.close()
    tmpFile = tempFH.name
    return tmpFile

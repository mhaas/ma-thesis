# -*- coding: utf-8 -*-

"""
This class is needed for the TigerXML parsing code in
nltk_contrib.
"""


class SimpleIndexer(object):

    def __init__(self):
        self.g = []

    def set_metadata(self, d):
        pass

    def set_edge_labels(self, d):
        pass

    def set_secedge_labels(self, d):
        pass

    def add_feature(self, name, domain, d):
        pass

    def add_graph(self, graph):
        self.g.append(graph)

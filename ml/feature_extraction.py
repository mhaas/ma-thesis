# -*- coding: utf-8 -*-

import csv
import codecs
import itertools
import logging
import re
import nltk
import numpy as np
import pickle


from shared import ma_util
from nltk.tag.stanford import POSTagger
from nltk.text import TextCollection, Text
from nltk.util import LazyConcatenation
from nltk.util import bigrams
from sklearn.feature_extraction import DictVectorizer
logger = logging.getLogger('feature_extraction')

NEG_LABEL_CONSTANT = -1
POS_LABEL_CONSTANT = 1
NEU_LABEL_CONSTANT = 0


class GenericLexiconExtractor(object):

    def __init__(self):
        raise NotImplemented('Abstract class')

    def getScore(self, somePhrase):
        """
        Gets score for a single phrase.
        The phrase is tokenized first and the individual
        tokens are looked up in both positive and negative dictionaries.

        Returns a tuple containing negative and positive score.

        @param somePhrase {string} a phrase to be looked up
        @returns {tuple{float,float}} negative and positive score
        """
        # split member does not exist anymore?
        # TODO: the whole thing does not make sense,
        # just use tokenization provided by tree.

        if isinstance(somePhrase, list):
            tokens = somePhrase
        else:
            # Either you bring tokens or you bring a tokenizer
            tokens = self.split(somePhrase)
        posScore = 0.0
        negScore = 0.0
        # invariant: scores for negative tokens are < 0
        for token in tokens:
            # this is unicode country
            #assert isinstance(token, unicode)
            if not isinstance(token, unicode):
                token = token.decode('utf-8')
            if self.allLower:
                token = token.lower()
            if token in self.posDict:
                posScore += self.posDict[token]
            if token in self.negDict:
                negScore += self.negDict[token]
        return (negScore, posScore)

    def getCoarseSentiment(self, somePhrase):
        # probably supposed to ignore shifters?
        negScore, posScore = self.getScore(somePhrase)
        overall = negScore + posScore
        if overall < 0:
            return ma_util.NEG
        elif overall == 0:
            return ma_util.NEU
        else:
            return ma_util.POS

    def getCoarseSentimentPOS(self, somePhrase):
        # probably supposed to ignore shifters?
        negScore, posScore = self.getScorePOS(somePhrase)
        overall = negScore + posScore
        if overall < 0:
            return ma_util.NEG
        elif overall == 0:
            return ma_util.NEU
        else:
            return ma_util.POS

    def getScorePOS(self, somePhrase):
        if not hasattr(self, "posDictP") and hasattr(self, "negDictP"):
            raise NotImplemented("no posDict found")
        if isinstance(somePhrase, list):
            tokens = somePhrase
        else:
            # Either you bring tokens or you bring a tokenizer
            tokens = self.split(somePhrase)
        posScore = 0.0
        negScore = 0.0
        for (posTag, token) in tokens:
            assert isinstance(token, unicode)
            mappedPos = self.posMapping.get(posTag[:3])
            if not mappedPos:
                logger.debug('No mapping found for POS %s', posTag)
                # continue
            if self.allLower:
                token = token.lower()
            if token in self.posDictP:
                if mappedPos in self.posDictP[token]:
                    posScore += self.posDictP[token][mappedPos]
            if token in self.negDictP:
                if mappedPos in self.negDictP[token]:
                    negScore += self.negDictP[token][mappedPos]
        return (negScore, posScore)


class KlennertExtractor(GenericLexiconExtractor):

    def __init__(self, lexiconFile, split=None):
        self.lex = lexiconFile
        self.split = split
        self.readSentiLex()
        self.posDict = self.sentiLexPos
        self.negDict = self.sentiLexNeg
        self.allLower = False

    def hasShifter(self, phrase):
        if isinstance(phrase, basestring):
            phrase = self.split(phrase)
        for token in phrase:
            if token in self.sentiLexShi:
                return True
        return False

    def readSentiLex(self):
        self.sentiLexPos = {}
        self.sentiLexNeg = {}
        self.sentiLexShi = {}
        self.sentiLexInt = {}
        fh = codecs.open(self.lex, u'r', u'utf-8')
        for line in fh:
            # handle comment
            if line.startswith('%%'):
                continue
            lineItems = line.split(u' ')
            token = lineItems[0]
            label = lineItems[1]
            labelItems = label.split(u'=')
            clazz = labelItems[0]
            value = float(labelItems[1])
            if clazz == 'POS':
                d = self.sentiLexPos
            elif clazz == 'NEG':
                d = self.sentiLexNeg
                value = 0 - value
            elif clazz == 'SHI':
                d = self.sentiLexShi
            elif clazz == 'INT':
                d = self.sentiLexInt
            elif clazz == 'NEU':
                pass
            else:
                raise ValueError('Unknown clazz %s' % clazz)
            d[token] = value
        fh.close()


class SentiWSExtractor(GenericLexiconExtractor):

    def __init__(self, phrasePredictor, sentiWSPosFile, sentiWSNegFile,
                 split=None):
        """
        @param phrasePredictor {PhrasePredictor} contains alphabet, model etc
        """
        self.pp = phrasePredictor
        # split used to live in pp.helper
        self.split = split
        self.posDict, self.posDictP = self.readSentiWS(
            sentiWSPosFile, getPos=True, lowerAll=False)
        self.negDict, self.negDictP = self.readSentiWS(
            sentiWSNegFile,  getPos=True, lowerAll=False)
        self.allLower = False
        # all verbs mapped to VVINF
        # other inflected forms are listed there as well!
        self.posMapping = {'ADJ': 'ADJX', 'ADV': 'ADV',
                           'VVF': 'VVINF', 'VVI': 'VVINF',
                           'VVA': 'VVINF',
                           'VVP': 'VVINF',
                           'VP': 'VVINF',
                           'NN': 'NN', 'NE': 'NN'}

    @staticmethod
    def readSentiWS(fileName, getPos=False, lowerAll=True):
        """Reads SentiWS file into a dict.

        Each word form becomes a dict key,
        the weight becomes the corresponding value.

        @param fileName {str} the path to the SentiWS file
        @returns {dict} Mapping from word form to weight
        """
        senLex = {}
        senLexP = {}
        fh = open(fileName)
        r = csv.reader(fh, delimiter='\t')
        for row in r:
            tokenPos = row[0].split("|")
            token = tokenPos[0]
            posTag = tokenPos[1]
            val = float(row[1])
            if len(row) > 2:
                forms = row[2].split(",")
            else:
                forms = []
            forms.append(token)
            for form in forms:
                form = form.decode("utf-8")
                if lowerAll:
                    form = form.lower()
                senLex[form] = val
                if not form in senLexP:
                    senLexP[form] = {}
                senLexP[form][posTag] = val
        if getPos:
            return (senLex, senLexP)
        else:
            return senLex

    def extract_sentiWS(self, goldSentence):
        """
        Extracts features from SentiWS.
        For each span in the goldSentence tree, the positive and negative
        weights (if any) are added in separate features.

        @param goldSentence {PTB tree} Parse tree with sentiment annotation
        @param posWords {dict} Mapping from positive word forms to weights
        @param negWords {dict} Mapping from negative word forms to weights
        @returns {tuple({list}, {list}} Positive and Negative features per span
        """
        pos = []
        neg = []
        for goldNode in ma_util.walkTree(goldSentence):

            (negScore,
             posScore) = self.getSentiWSScore(goldNode.leaves())
            pos.append(posScore)
            neg.append(negScore)
        return (pos, neg)

    def getSentiWSScore(self, somePhrase):
        return self.getScore(somePhrase)


class SentiMergeExtractor(GenericLexiconExtractor):

    PRECISION_THRESHOLD = 0.4
    RECALL_THRESHOLD = 0.23
    SILLY_THRESHOLD = 0.0

    def __init__(self, lexFile, split=None, threshold=SILLY_THRESHOLD):
        self.threshold = threshold
        self.lexFile = lexFile
        self.readSentiMerge()
        # from STTS to SentiMERGE
        # STTS truncated to 3 chars
        # VVFIN   finites Verb, voll                      [du] gehst, [wir]
        # kommen [an]
        # VVIMP   Imperativ, voll                         komm [!]
        # VVINF   Infinitiv, voll                         gehen, ankommen
        # VVIZU   Infinitiv mit ``zu'', voll            anzukommen, loszulassen
        # VVPP    Partizip Perfekt, voll                  gegangen, angekommen
        # VAFIN   finites Verb, aux                     [du] bist, [wir] werden
        # VAIMP   Imperativ, aux                         sei [ruhig !]
        self.posMapping = {'ADJ': 'AJ', 'ADV': 'AV',
                           'VVF': 'V', 'VVI': 'V',
                           'VVA': 'V',
                           'VVP': 'V',
                           'VP': 'V',
                           'NN': 'N', 'NE': 'N'}
        self.allLower = True

    def readSentiMerge(self):
        # csv has some trouble with unicode
        # so process byte string decode later
        fh = open(self.lexFile)
        reader = csv.DictReader(fh, delimiter='\t')
        self.posDict = {}
        self.negDict = {}
        self.posDictP = {}
        self.negDictP = {}
        for row in reader:
            # lemma   PoS     sentiment       weight
            token = row['lemma'].decode('utf-8')
            sentiment = float(row['sentiment'])
            pos = row['PoS']
            if sentiment < 0:
                d = self.negDict
                dP = self.negDictP
            else:
                d = self.posDict
                dP = self.posDictP
            if abs(sentiment) < self.threshold:
                sentiment = 0.0
            # Yes, this will override previous lemmas with different POS
            d[token] = sentiment
            if not token in dP:
                dP[token] = {}
            dP[token][pos] = sentiment
        return fh.close()


class GermanPolarityCluesExtractor(GenericLexiconExtractor):

    def __init__(self, posFile, negFile, split=None):
        # pos in the full file, not the lemmatized versions
        self.posDict, self.posDictP = self.readGPC(posFile)
        self.negDict, self.negDictP = self.readGPC(negFile)
        self.split = split
        self.allLower = False
        # So, adverbs seem to be in the 'AD' category as well
        # e.g. 'zwangsweise'
        # I opt to leave out adjectives completely as a modelling decision
        # e.g. i assume 'AD' always means 'ADJ'.
        self.posMapping = {'ADJ': 'AD',
                           'VVF': 'VVINF', 'VVI': 'VVINF',
                           'VVA': 'VV',
                           'VVP': 'VV',
                           'VP': 'VV',
                           'NN': 'NN', 'NE': 'NN'}

    def readGPC(self, fileName):
        # Abandon Abandon NN      negative        -/-/-   DOB
        fieldNames = ['token', 'lemma', 'pos', 'polarity', 'distribution',
                      'someLabel']
        # we want the regular files here, not the *lemma*.tsv versions
        fh = open(fileName)
        reader = csv.DictReader(fh, delimiter='\t', fieldnames=fieldNames)
        polarityDict = {}
        polarityDictP = {}
        for row in reader:
            token = row['token'].decode('utf-8')
            pos = row['pos']
            sentiment = row['polarity']
            if sentiment == 'negative':
                # must be negative!
                label = NEG_LABEL_CONSTANT
            elif sentiment == 'positive':
                label = POS_LABEL_CONSTANT
            elif sentiment == 'neutral':
                # not sure why you would want that...
                label == NEU_LABEL_CONSTANT
            else:
                raise ValueError('Unknown sentiment label %s' % sentiment)
            polarityDict[token] = label
            if token not in polarityDictP:
                polarityDictP[token] = {}
            polarityDictP[token][pos] = label
        return (polarityDict, polarityDictP)


class MznMLExtractor(GenericLexiconExtractor):
    # this class is similar to PhrasePredictorExtractor,
    # but with less indirection and silliness
    # most importantly, it plugs into the
    # LexiconExtractor framework and does not carry as much
    # baggage
    def __init__(self, alphabet, model):
        self.allLower = True
        self.alphabet = pickle.load(open(alphabet))
        self.model = pickle.load(open(model))
        self.posDict = {}
        self.negDict = {}
        if not hasattr(self.model, "coef_"):
            self.coef_vector = self.model.scores_
        else:
            self.coef_vector = self.model.coef_
        # some classifiers provide one vector per class
        if len(self.coef_vector) == 1:
            self.coef_vector = self.coef_vector[0]
        self.reverse_alphabet = {}
        self.readLexicon()

    def readLexicon(self):
        for (token, index) in self.alphabet.iteritems():
            print type(token)
            value = self.coef_vector[index]
            print "token %s at index %s has value %.15g" % (token, index,
                                                            value)
            if value > 0:
                self.posDict[token] = value
            else:
                self.negDict[token] = value
            # TODO: allLower?


class ProjectionExtractor(object):

    def __init__(self, granularity=ma_util.GRANULARITY_COARSE):
        self.granularity = granularity

    def extract_projection_sentiment(self, tigerObj, tigerSentence):
        """Extracts projection feature.

        @param tigerObj {TigerXML} Full parse file
        @param tigerSentence {some XML Element} XML node of current sentence
        @returns {list} Sentiment Values for each Span NEG, NEU, POS
        """
        data = []
        for node in tigerObj.preOrder(tigerSentence, forceSentiment=True):
            data.append(ma_util.sen(node[1], self.granularity))
        return data


class GoldExtractor(object):

    def __init__(self, granularity=ma_util.GRANULARITY_COARSE):
        self.granularity = granularity

    def extract_gold_sentiment(self, goldSentence, extractLength=False):
        """Extracts gold label.

        @param goldSentence {PTB tree} Parse tree with sentiment annotation
        @returns {list} List of labels
        """
        data = []
        for goldNode in ma_util.walkTree(goldSentence):
            label = ma_util.sen(goldNode.node, self.granularity)
            if extractLength:
                data.append((label, len(goldNode.leaves())))
            else:
                data.append(label)
        return data

    def extract_gold_from_trees(self, trees):
        res = []
        ge = GoldExtractor(granularity=self.granularity)
        for tree in trees:
            res.extend(ge.extract_gold_sentiment(tree))
        return np.asarray(res, dtype=np.int)


class PhrasePredictorExtractor(object):

    def __init__(self, phrasePredictor):
        """
        @param phrasePredictor {PhrasePredictor} contains alphabet, model, etc
        """
        self.pp = phrasePredictor

    def extract_phrase_predictor_sentiment(self, goldSentence,
                                           returnSpans=False):
        """Extracts features from PhrasePredictor.

        The PhrasePredictor returns three features:
            - ScoreSum - sum over learned word weights
            - RegressionScore - predicted Amazon Review Star Rating
            - Token count
        @param goldSentence {PTB tree} Parse tree with sentiment annotation
        @returns {tuple} 3-tuple of lists with features
        """
        data = []
        data2 = []
        counts = []
        spans = []
        for goldNode in ma_util.walkTree(goldSentence):
            ppSpan = self.pp.getSpan(goldNode)
            ppSentiment = self.pp.main(ppSpan, True)
            sentiString = self.pp.score_sum_to_sentiment(ppSentiment[0])
            data.append(ma_util.strSen(sentiString))
            # this works almost as well (to the point of the difference
            # likely being noise), and the feature importance is
            # bit more evenly distributed with the original sumscore
            # instead of the discretized version
            # data.append(ppSentiment[0])
            data2.append(ppSentiment[1])
            # counts.append(ppSentiment[2])
            counts.append(len(goldNode.leaves()))
            spans.append(ppSpan)
        if returnSpans:
            return (data, data2, counts, spans)
        else:
            return (data, data2, counts)


class POSExtractor(object):

    def __init__(self, gold, toClassify,
                 base="/resources/processors/tagger/stanford-postagger-3.0/"):
        self.posTagger = POSTagger(base + "/models/german.tagger",
                                   base + "/stanford-postagger.jar")
        self.posCache = {}
        self.pos_dv = self._trainPOSDictVectorizer(gold, toClassify)

    def _trainPOSDictVectorizer(self, goldTree, to_classify=None):
        sentences = list(goldTree)
        if to_classify:
            sentences.extend(to_classify)
        pos_tagged = self.get_pos_tags_for_sentences(sentences)
        items = []
        assert len(pos_tagged) == len(sentences)
        for sentence, pos in itertools.izip(sentences, pos_tagged):
            # feels silly, but there is the occasional encoding error
            # when using str(sentence)
            self.posCache[sentence.pprint().encode('utf-8')] = pos
            items.extend(self.extract_POS(sentence, pos))
        dv = DictVectorizer(sparse=False)
        dv.fit(items)
        #logger.debug("DictVectorizer vocab: %s", dv.vocabulary_)
        return dv

    def get_pos_tags_for_sentences(self, sentences):
        tokenizedSentences = []
        for parseTree in sentences:
            tokens = parseTree.leaves()
            #  (PROAV Deshalb)
            #  (@S-:-PROAV-..
            #      (@S-:-PROAV-...-$.
            #             (VVFIN 3 1/2)
            #             (NP-SB (NN Sterne) (PP (APPR von) (PPER mir))))
            #      ($. .)))
            # [('Deshalb', 'PROAV'), ('3', 'CARD'), ('1/2', 'CARD')
            #
            # encode as utf-8
            # the POSTagger object hands this over to a separate object,
            # i.e. at some point str() is called on the tokens
            tokens = map(lambda x: x.encode('utf-8'), tokens)
            # 3 1/2 is separated by a non-breaking space which prevented
            # correct tokenization in the parse tree
            # the pos tagger however breaks it up correctly
            # so replace 3 1/2 with 3-1/2
            tokens = map(lambda x: x.replace('3\xc2\xa01/2', '3-1/2'), tokens)
            tokenizedSentences.append(tokens)
        pos_tagged = self.posTagger.batch_tag(tokenizedSentences)
        assert len(pos_tagged) == len(tokenizedSentences)
        return pos_tagged

    def transform(self, posTag):
        return self.pos_dv.transform(posTag)

    def extract_POS(self, goldSentence, tagged=None):
        if tagged is None:
            tagged = self.posCache[goldSentence.pprint().encode('utf-8')]
        if tagged is None:
            #tagged = self.get_pos_tags_for_sentences([goldSentence])[0]
            raise ValueError("Should have seen sentence in cache: %s" %
                             goldSentence)
        leaves = goldSentence.leaves()
        if not len(leaves) == len(tagged):
            logger.error("leaves do not correspond to tagged!")
            logger.error("leaves: %s, tagged: %s", leaves, tagged)
        # TODO: there's a chance that similar leaves will have their POS tags
        # overriden
        # but yeah, good enough for now.
        leafDict = {}
        for (leaf, pos) in itertools.izip(leaves, tagged):
            pos = pos[1]
            leafDict[leaf] = pos
        items = []
        all_pos_tags = set()
        for goldNode in ma_util.walkTree(goldSentence):
            res = {}
            for subTreeLeaf in goldNode.leaves():
                key = leafDict[subTreeLeaf]  # [0]
                if not key in res:
                    res[key] = 0
                res[key] += 1  # += 1
                all_pos_tags.add(key)
            items.append(res)
        return items


class TokenExtractor(object):

    LANG_EN = 'english'
    LANG_DE = 'german'

    def __init__(
        self, documents, unigrams, bigrams=False, gappyBigrams=False,
            useTfIdf=False, useFrequencies=False,
            skipSingletons=False, lang=LANG_DE, alphabetSize=None,
            documentsAreSentences=False):
        # if documentsAreSentences, then there is no need to run
        # a sentence splitter
        # only used for text.
        if documentsAreSentences:
            self.sentence_splitter = lambda x: [x]
        else:
            self.sentence_splitter = nltk.data.load('tokenizers/punkt/'
                                                    + lang + '.pickle')
        self.sentence_tokenizer = nltk.tokenize.TreebankWordTokenizer()
        assert self.sentence_splitter
        self.useTfIdf = useTfIdf
        self.tfIdf = None
        self.skipSingletons = skipSingletons
        self.alphabetSize = alphabetSize
        self.unigrams = unigrams
        self.bigrams = bigrams
        self.gappyBigrams = gappyBigrams
        self.useFrequencies = useFrequencies
        self.__build_alphabet(documents)

    @staticmethod
    def split_rest(tokens):
        u"""NLTK tokenizer does not tokenize everything correctly.
        >>> TokenExtractor.split_rest(["ich.und", "hallo"])
        ['ich', 'und', 'hallo']
        >>> TokenExtractor.split_rest(["'ich.und", "hallo_", 'test!'])
        ['ich', 'und', 'hallo_', 'test']
        >>> TokenExtractor.split_rest([u"'ästhetischen"])
        [u'\\xe4sthetischen']
        >>> TokenExtractor.split_rest([u"'ästhetischen.keks"])
        [u'\\xe4sthetischen', u'keks']
        """
        res = []
        noise_re = re.compile(ur'[^\w\.]', re.UNICODE)
        regex = re.compile(ur'(\w+)\.(\w+)', re.UNICODE)
        for token in tokens:
            token = noise_re.sub("", token)
            m = regex.match(token)
            if m:
                res.append(m.group(1))
                res.append(m.group(2))
            else:
                res.append(token)
        return res

    def trees_to_vectors(self, trees):
        # list of trees
        vectors = None
        for tree in trees:
            # returns a horizontally stacked scipy.sparse.csr_matrix
            # and we combine these again
            vec = self.extract_xgrams_from_tree(tree)
            if vectors is None:
                # is already a 2d array.
                vectors = vec
            else:
                vectors = np.concatenate([vectors, vec])
        return vectors

    def extract_xgrams_from_tree(self, tree):
        # a tree is a single document
        # returns a horizontally stacked scipy.sparse.csr_matrix
        vectors = None
        for subTree in ma_util.walkTree(tree):
            xgrams = self.handleGrams(subTree.leaves())
            vec = self.convert_document_to_vector(xgrams)
            if vectors is None:
                # make 2d array
                vectors = np.asarray([vec])
            else:
                vectors = np.concatenate([vectors, [vec]])
        return vectors

    def convert_multiple_documents_to_vectors(self, documents):
        vectors = None
        for document in documents:
            vec = self.convert_document_to_vector(self.split(document))
            if vectors is None:
                # make 2d array
                vectors = np.asarray([vec])
            else:
                vectors = np.concatenate([vectors, [vec]])
        return vectors

    def convert_document_to_vector(self, tokenList):
        res = []
        # faster lookup time
        if not (self.useTfIdf or self.useFrequencies):
            tokenList = set(tokenList)
        for x in xrange(len(self.reverse_alphabet)):
            token = self.reverse_alphabet[x]
            if self.useTfIdf:
                value = self.tfIdf.tf_idf(token, tokenList)
            elif self.useFrequencies:
                value = tokenList.count(token)
            else:
                if token in tokenList:
                    value = 1
                else:
                    value = 0
            res.append(float(value))
        # This should save memory, but I have trouble handling those
        # For some consumers, sparse matrices need to be converted to dense
        # m = scipy.sparse.csr_matrix(res)
        return np.asarray(res, dtype=np.float)

    @staticmethod
    def clean(token):
        token = token.strip()
        token = token.lower()
        return token

    @staticmethod
    def gappy_bigrams(text):
        """
        >>> TokenExtractor.gappy_bigrams(["A", "B", "C"])
        [('A', 'C')]
        >>> TokenExtractor.gappy_bigrams(['A', 'B', 'C', 'D'])
        [('A', 'C'), ('B', 'D')]
        """
        bg = bigrams(text)
        last = None
        res = []
        for (w1, w2) in bg:
            if last is not None:
                gappy = (last[0], w2)
                res.append(gappy)
            last = (w1, w2)
        return res

    def split(self, document):
        """Tokenizes an entire document."""
        splitted = []
        for sentence in self.sentence_splitter.tokenize(document):
            for token in self.sentence_tokenizer.tokenize(sentence):
                cleaned = self.clean(token)
                if cleaned == "":
                    continue
                splitted.append(cleaned)
        splitted = self.split_rest(splitted)
        return self.handleGrams(splitted)

    def handleGrams(self, tokenList):
        res = []
        if self.unigrams:
            res.extend(tokenList)
        if self.bigrams:
            res.extend(bigrams(tokenList))
        if self.gappyBigrams:
            res.extend(self.gappy_bigrams(tokenList))
        return res

    def __build_alphabet(self, documents):
        if len(documents) == 0:
            return
        firstDoc = documents[0]
        if isinstance(firstDoc, nltk.tree.Tree):
            documents = self.__tokenize_trees(documents)
        else:
            documents = self.__tokenize_text(documents)
        self.__build_alphabet_from_tokens(documents)

    def __tokenize_text(self, documents):
        res = []
        for document in documents:
            curDoc = []
            for token in self.split(document):
                curDoc.append(token)
            res.append(curDoc)
        return res

    def __tokenize_trees(self, documents):
        res = []
        for tree in documents:
            curDoc = tree.leaves()
            res.append(curDoc)
        return res

    def __build_alphabet_from_tokens(self, documents):
        logger.info("Building alphabet")
        if self.useTfIdf:
            logger.info("Building counts for TF-IDF")
            documentCollection = []
        res = {}
        counts = {}
        for document in documents:
            if self.useTfIdf:
                currentDocument = []
                documentCollection.append(currentDocument)
            for token in document:
                #logger.debug("Token: %s, Document: %s", token, document)
                if self.useTfIdf:
                    currentDocument.append(token)
                if token not in counts:
                    counts[token] = 0
                counts[token] += 1
        if self.useTfIdf:
            self.tfIdf = NotSoBrokenTextCollection(documentCollection,
                                                   name="TFIDF")
        logger.info("Got %s tokens" % len(counts))
        if self.skipSingletons:
            logger.info("Removing Hapax Legomena from alphabet")
            for (token, count) in counts.items():
                if count == 1:
                    logger.debug("Hapax legomenon: %s", token)
                    del counts[token]
            logger.info("Removed Hapax Legomena, now %s tokens", len(counts))
        else:
            logger.info("Not removing Hapax Legomena")
        # sorted tokens by frequency, retain most frequent K tokens
        truncated = sorted(counts.items(), key=lambda (token, count): count,
                           reverse=True)
        truncated = truncated[:self.alphabetSize]
        self.reverse_alphabet = []
        for index in xrange(len(truncated)):
            token = truncated[index][0]
            self.reverse_alphabet.append(token)
            res[token] = index
        # mapping from tokens to indices.
        # Needed for some other applications, so do not remove.
        self.alphabet = res
        logger.info("Truncated to %s", len(res))
        logger.debug("alphabet is: %s", self.alphabet)
        for x in xrange(len(self.reverse_alphabet)):
            logger.debug("reverse_alphabet at %s: %s", x,
                         self.reverse_alphabet[x])


class NotSoBrokenTextCollection(TextCollection):

    def __init__(self, source, name=None):
        if hasattr(source, 'words'):
            source = [source.words(f) for f in source.fileids()]
        self._texts = source
        Text.__init__(self, LazyConcatenation(source), name)
        self._idf_cache = {}

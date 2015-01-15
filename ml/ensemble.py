#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script does all kinds of ensemble learning with the
# goal of predicting trinary sentiment labels or binary
# subjectivity/objectivity labels.

import argparse
import itertools
import tigerhelper as th
from evaluate_coef_sentiment_prediction import PhrasePredictor
import yaml
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.cross_validation import StratifiedKFold
import numpy
import pickle
import os
import logging
from shared import evaluate
import feature_extraction
import csv
import ma_util

logger = logging.getLogger('ensemble')

from shared.ma_util import NEU, POS, NEG


# features
PROJ = "projection"
SENTIWS = "sentiws"
REGSCORE = "regressionscore"
COUNT = "count"
PHRASES = "phrasesentiment"
POSF = "postags"

FEATURE_ORDER = [PHRASES, PROJ, REGSCORE, COUNT, SENTIWS, POSF]

# learners
LINSVC = "SVC_linear"
RFC = "RandomForest"
ABC = "AdaBoost"
GBC = "GradientBoosting"
ETC = "ExtraTrees"


class EnsembleLearner(object):

    def __init__(self, features, goldFile, projectedFile, foldsFile,
                 mznAlphabet, mznModel, mznArgs,
                 sentiWSPos, sentiWSNeg, toClassifyFile, toClassifyProjFile,
                 toClassifyOutFile, toClassifyIsTest, doCV, evalCSV,
                 weightsCSV, learners):
        """
        @param features {iterable{string}} List of features
        @param goldFile Filename of gold sentences (PTB format)
        @param projectedFile Filename of projected trees (TigerXML)
        @param mznAlphabet Alphabet file (Pickle) (see PhrasePredictor)
        @param mznModel Model file (Pickle) (see PhrasePredictor)
        @param mznArgs Argsparse dump (Pickle) (see PhrasePredictor)
        @param sentiWSPos SentiWS file with positive words
        @param sentiWSNeg SentiWS file with negative words
        """
        self.sentiWSPos = sentiWSPos
        self.sentiWSNeg = sentiWSNeg
        self.features = features
        self.goldFile = goldFile
        self.gold = ma_util.readPenn(goldFile)
        self.projectedFile = projectedFile
        self.foldsFile = foldsFile
        self.pp = PhrasePredictor(mznAlphabet, mznModel, mznArgs, False)
        self.toClassifyFile = toClassifyFile
        self.toClassify = None
        if self.toClassifyFile:
            self.toClassify = list(ma_util.readPenn(self.toClassifyFile))
        self.toClassifyProjFile = toClassifyProjFile
        self.toClassifyOutFile = toClassifyOutFile
        self.toClassifyIsTest = toClassifyIsTest
        self._init_extractors()
        # re-init
        self.gold = ma_util.readPenn(goldFile)
        self.doCV = doCV
        self.learners = learners
        self.evalCSV = evalCSV
        self.weightsCSV = weightsCSV
        # eval data is stored and written once we're done
        self.evalData = []
        self.weightsData = []
        self._load_data()

    def _load_data(self):
        """
        Loads parse trees and extracts features.
        """
        (self.trainData,
         self.trainLabels,
         self.trainRootInd) = self.extract_features(self.gold,
                                                    self.projectedFile,
                                                    True)
        if self.toClassifyFile:
            (self.testData,
             self.testLabels,
             self.testRootInd) = self.extract_features(self.toClassify,
                                                       self.toClassifyProjFile,
                                                       self.toClassifyIsTest)

    def save_data(self, outFile):
        """
        Saves extracted vector data to disk.
        The file will contain a YAML dump of a dictionary.

        @param outFile {string} File name of output file
        """
        full_data = {'data': self.trainData,
                     'labels': self.trainLabels}
        if self.toClassify:
            full_data["to_be_classified"] = self.testData
        if self.toClassifyIsTest:
            full_data['to_be_classified_labels'] = self.testLabels
        fh = open(outFile, 'w')
        yaml.dump(full_data, fh)
        fh.close()

    def _init_extractors(self):
        """
        Sets up extractor objects.
        """
        if POSF in self.features:
            self.posE = feature_extraction.POSExtractor(self.gold,
                                                        self.toClassify)
        if SENTIWS in self.features:
            self.sentiWSE = feature_extraction.SentiWSExtractor(
                self.pp,
                self.sentiWSPos,
                self.sentiWSNeg)
        if PROJ in self.features:
            self.projE = feature_extraction.ProjectionExtractor()
        if (REGSCORE in self.features or COUNT in self.features
                or PHRASES in self.features):
            self.ppE = feature_extraction.PhrasePredictorExtractor(self.pp)
        self.goldE = feature_extraction.GoldExtractor()

    def extract_features(self, trees, projected, extractLabels):
        """
        Turns a set of parse trees into feature vectors.

        @param trees {Iterable<nltk.tree.Tree>} Source data
        @param projected {basestring} Filename of projected trees (TigerXML)
        @param extractLabels {bool} Whether to return node labels or not
        @returns {tuple} Tuple of lists for features and labels
        """
        projectedSentences = []
        if PROJ in self.features:
            projectedTiger = th.TigerHelper(projected)
            projectedSentences = th.getSentences(projectedTiger.tree)
        nodeLabels = []
        data = []
        rootIndices = []
        for (projectedSentence,
             treeSentence) in itertools.izip_longest(projectedSentences,
                                                     trees,
                                                     fillvalue=
                                                     "LISTLEN_NEQ"):
            if projectedSentence == "LISTLEN_NEQ":
                raise ValueError("projectedSentences too short!")
            if treeSentence == "LISTLEN_NEQ":
                raise ValueError("trees too short!")
            rootIndices.append(len(data))
            # Variables are only set if features are to be extracted
            projS = None
            labelsS = None
            sentiWSPosS = None
            sentiWSNegS = None
            pos = None
            (phraseS,
             regScores,
             counts) = self.ppE.extract_phrase_predictor_sentiment(
                treeSentence)
            if PROJ in self.features:
                projS = self.projE.extract_projection_sentiment(
                    projectedTiger,
                    projectedSentence)
            # Does the tree contain gold or is it just any old tree?
            # To clarify: a tree is not necessarily annotated with a sentiment
            # label. It could also be a vanilla parse tree.
            if extractLabels:
                labelsS = self.goldE.extract_gold_sentiment(treeSentence)
                assert len(labelsS) == len(phraseS)
            if SENTIWS in self.features:
                (sentiWSPosS,
                 sentiWSNegS) = self.sentiWSE.extract_sentiWS(treeSentence)
            if POSF in self.features:
                pos = self.posE.extract_POS(treeSentence)
            vectors = self.build_item_vectors(phraseS, projS,
                                              regScores, counts,
                                              sentiWSPosS, sentiWSNegS, pos)
            data.extend(vectors)
            if extractLabels:
                nodeLabels.extend(labelsS)
        return (numpy.asarray(data), numpy.asarray(nodeLabels), rootIndices)

    def build_item_vectors(self, phraseS, projS, regScores, counts,
                           sentiWSPosS, sentiWSNegS, pos):
        """
        Constructs vectors from extracted data.
        The extracted features are passed in as one list per feature.
        Each list position corresponds to a single data item, i.e. a parse
        tree span.

        Note: the dicts contained in the pos parameter iterable will be
        encoded.

        @param phraseS {Iterable<int>} Sentiment label based on Amazon lexicon
        @param projS {Iterable<int>} Projected sentiment label
        @param regScores {Iterable<float>} Predicted review score
        @param counts {Iterable<int>} Token count
        @param sentiWSPosS {Iterable<float>} Semantic Orientation (pos SentiWS)
        @param sentiWSNegS {Iterable<float>} Semantic Orientation (neg SentiWS)
        @param pos {Iterable<dict>} Part-of-Speech tags
        """
        data = []
        for index in xrange(len(phraseS)):
            curItem = []
            if PHRASES in self.features:
                phrase = phraseS[index]
                curItem.append(phrase)
            if PROJ in self.features:
                assert len(projS) == len(phraseS)
                proj = projS[index]
                curItem.append(proj)
            if REGSCORE in self.features:
                assert len(regScores) == len(phraseS)
                regScore = regScores[index][0]
                curItem.append(regScore)
            if COUNT in self.features:
                assert len(counts) == len(phraseS)
                #raise ValueError("Count feature is broken!")
                tokenCount = counts[index]
                curItem.append(tokenCount)
            if SENTIWS in self.features:
                assert len(sentiWSPosS) == len(phraseS)
                assert len(sentiWSNegS) == len(phraseS)
                curItem.append(sentiWSPosS[index])
                curItem.append(sentiWSNegS[index])
            if POSF in self.features:
                curItem.extend(self.posE.transform(pos[index])[0])
            data.append(curItem)
        return data

    def build_classifier(self):
        """
        Creates classifier objects and tests them.
        """
        if RFC in self.learners:
            rfc = RandomForestClassifier()
            self.test_classifier(rfc, RFC)
        if ABC in self.learners:
            adab = AdaBoostClassifier()
            self.test_classifier(adab, ABC)
        if GBC in self.learners:
            grad = GradientBoostingClassifier()
            self.test_classifier(grad, GBC)
        if LINSVC in self.learners:
            linsvc = SVC(kernel="linear")
            self.test_classifier(linsvc, LINSVC)
        if ETC in self.learners:
            extrat = ExtraTreesClassifier()
            self.test_classifier(extrat, ETC)

    def get_feature_importances_header(self):
        """
        Generates a list of field names for the feature importances
        CSV file.
        """
        # features in the order in which they appear in the vector
        header = ["name"]
        for feature in FEATURE_ORDER:
            if feature == SENTIWS:
                header.append(feature + 'PosImportance')
                header.append(feature + 'NegImportance')
            elif feature == POSF:
                header.append(feature + 'SumImportance')
            else:
                header.append(feature + 'Importance')
        return header

    def get_feature_importances(self, name, classifier):
        """
        Looks up feature weights and prepares them for reporting.

        Some, but not all, learners have a feature_importances_ member
        which basically lists the importance of individual features.

        This method maps the vector indices back to feature names.
        The SentiWS feature generates two vector entries (positive and
        negative).

        The POS feature is really a class of features. All POS-based features
        are merged into a single feature when reporting the importance.

        The weights are added to the EnsembleLearner::weightsData list
        which can be serialized using the EnsembleLearner::write_eval_data()
        method.

        If a feature is not used, -1 is used as weight.
        If the learner does not support feature importances reporting,
        -2 is reported for all features.

        @param name {string} Name of the classifier or run
        @param classifier {sklearn Classifier} Classifier instance
        """
        importances = [name]
        if not hasattr(classifier, "feature_importances_"):
            importances = [-2 for x in xrange((len(FEATURE_ORDER) + 1))]
            self.weightsData.append(importances)
        fA = classifier.feature_importances_
        importancesIndex = 0
        for feature in FEATURE_ORDER:
            if feature in self.features:
                if feature == POSF:
                    # POSF contributes more than one feature
                    val = sum(fA[importancesIndex:])
                elif feature == SENTIWS:
                    importances.append(fA[importancesIndex])
                    importancesIndex += 1
                    val = fA[importancesIndex]
                else:
                    val = fA[importancesIndex]
                importancesIndex += 1
            else:
                val = -1
            importances.append(val)
        self.weightsData.append(importances)

    def _write_feature_imp_csv(self):
        """
        Serializes feature weights to disk.
        """
        fh = open(self.weightsCSV, 'w')
        writer = csv.writer(fh)
        writer.writerow(self.get_feature_importances_header())
        writer.writerows(self.weightsData)
        fh.close()

    def load_folds(self):
        """
        Loads CV folds from disk. If folds file does not exist,
        a new split is generated and saved to disk.

        This is only useful for CV mode.
        """
        if not self.foldsFile:
            logger.warn('self.foldsFile not set. Disable either --do-cv'
                        + ' or --folds.')
        folds = None
        if not os.path.exists(self.foldsFile):
            fh = open(self.oldsFile, 'w')
            folds = StratifiedKFold(self.trainLabels, n_folds=10)
            pickle.dump(folds, fh)
            fh.close()
            logger.info('Folds file did not exist!')
        else:
            fh = open(self.foldsFile)
            folds = pickle.load(fh)
            fh.close()
            logger.info('Folds successfully loaded from file.')
        return folds

    def test_classifier(self, classifier, name):
        """
        Trains a given classifier.
        The classifier can be evaluated in a cross-validation setting.
        If an additional set of data is available, labels for this data can
        be predicted. If the data contains gold labels, evaluation is
        possible.

        @param name {string} Name of the classifier or run
        @param classifier {sklearn Classifier} Classifier instance
        """
        if self.doCV:
            self.test_classifier_cv(classifier, name)
        if self.toClassify:
            self.test_classifier_toClassify(classifier, name)

    def test_classifier_cv(self, classifier, name):
        """
        Performs 10-fold cross-validation on the given classifier.

        @param name {string} Name of the classifier or run
        @param classifier {sklearn Classifier} Classifier instance
        """
        folds = self.load_folds()
        if not folds:
            logger.error("Folds is None?")
        # Does not handle root nodes separately as the folds do not distinguish
        # between these
        # So what we do here: collect all results, i..e all csv rows for all
        # folds, and print two files with 10 lines each
        logger.info("test_classifier: %s", classifier)
        foldNum = 0
        for train_index, test_index in self.folds:
            logger.debug("Current fold: train_index: %s", train_index)
            logger.debug("Current fold: test_index: %s", test_index)
            classifier.fit(self.trainData[train_index],
                           self.trainLabels[train_index])
            pred = classifier.predict(self.trainData[test_index])

            allEval = evaluate.printStatsCoarseInt(
                self.trainLabels[test_index],
                pred)
            allEval = evaluate.ins(['Classifier', 'Mode', 'Fold'],
                                   [name, 'CV', foldNum],
                                   allEval)
            self.evalData.append(allEval)
            # mangle name to include other columns
            self.get_feature_importances(name + '-CV-Fold-' + foldNum,
                                         classifier)
            foldNum += 1

    def test_classifier_toClassify(self, classifier, name):
        """
        Trains classifier on EnsembleLearner::trainData and
        predicts labels for EnsembleLearner::testData.
        The predictions are saved as a tree to the location specified by
        EnsembleLearner::toClassifyOutFile.

        If EnsembleLearner::toClassifyIsTest is set, the labels
        in EnsembleLearner::testLabels are used to evaluate the
        predictions.


        @param name {string} Name of the classifier or run
        @param classifier {sklearn Classifier} Classifier instance
        """
        logger.info("Started classifying file")
        logger.debug("len(data): %s" % len(self.trainData))
        logger.debug("len(labels): %s" % len(self.trainLabels))
        classifier.fit(self.trainData, self.trainLabels)
        self.get_feature_importances(name + '-Single', classifier)
        pred = classifier.predict(self.testData)
        out = open(self.toClassifyOutFile, "w")
        trees = self.apply_prediction_to_tree(
            self.toClassify, pred.tolist())
        for tree in trees:
            # .encode('utf-8'))
            out.write(tree.pprint(margin=999999, nodesep='').encode('utf-8'))
            out.write('\n')
        out.close()
        logger.info("Finished classifying file")
        if self.toClassifyIsTest:
            rootPred = numpy.asarray(pred)[self.testRootInd]
            rootGold = numpy.asarray(self.testLabels)[self.testRootInd]
            rootEval = evaluate.printStatsCoarseInt(rootGold,
                                                    rootPred,
                                                    "root")
            allEval = evaluate.printStatsCoarseInt(self.testLabels,
                                                   pred)
            allEval.update(rootEval)
            allEval = evaluate.ins(['Classifier', 'Mode', 'Fold'],
                                   [name, 'Single', 'N/A'],
                                   allEval)
            self.evalData.append(allEval)

    @staticmethod
    def apply_prediction_to_tree(trees, predictions,
                                 predGranularity=ma_util.GRANULARITY_COARSE):
        """
        Applies a list of predictions to a list of parse trees.

        Each entry in the prediction list corresponds to a subtree
        in the list of parse trees.

        The predictions can be either GRANULARITY_COARSE or GRANULARITY_FINE.
        GRANULARITY_COARSE predictions are mapped back into the GRANULARITY_FINE
        space. The resulting trees will always have labels ranging from
        VERY_NEG to VERY_POS.

        @param trees {Iterable<nltk.tree.Tree>} Parse trees
        @param predGranularity {str} GRANULARITY_COARSE or GRANULARITY_FINE
        @param predictions {Iterable<int>} List of predictions
        """
        subTrees = []
        for tree in trees:
            subTrees.extend(tree.subtrees())
        assert len(subTrees) == len(predictions)
        for (tree, prediction) in itertools.izip_longest(subTrees,
                                                         predictions):
            if predGranularity == ma_util.GRANULARITY_COARSE:
                if prediction == NEG or prediction == "neg":
                    prediction = ma_util.VERY_NEG
                elif prediction == NEU or prediction == "neu":
                    prediction = ma_util.FINE_NEU
                elif prediction == POS or prediction == "pos":
                    prediction = ma_util.VERY_POS
                else:
                    raise ValueError("Unknown pred label: %s" % prediction)
            tree.node = str(int(prediction))
        return trees

    def write_eval_data(self):
        """
        Saves eval data to disk as CSV files.

        The evaluation metrics from EnsembleLearner::evalData
        are saved to EnsembleLearner::evalCSV.

        Feature importances are handled by
        EnsembleLearner::_write_feature_imp_csv().
        """
        evaluate.statsToFile(self.evalData, self.evalCSV, multi=True)
        self._write_feature_imp_csv()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Combine output of several classifiers'
                    + 'into meta-classifier')
    parser.add_argument('--gold', required=True,
                        help='Gold PTB file')
    parser.add_argument('--projected',
                        help='TigerXML file containing result of projection')
    parser.add_argument('--mzn-reg-alphabet', required=True,
                        help='Alphabet of MZN regression model')
    parser.add_argument('--mzn-reg-model', required=True,
                        help='Learner object of MZN regression model')
    parser.add_argument('--mzn-reg-args', required=True,
                        help='Argsparse object of MZN reg model')
    parser.add_argument('--sentiws-pos', required=True,
                        help='SentiWS file with positive words.')
    parser.add_argument('--sentiws-neg', required=True,
                        help='SentiWS file with negative words.')
    parser.add_argument('--folds',
                        help='Pickled folds file. Need to change for different'
                        + ' --gold files!')
    parser.add_argument('--save-vectors',
                        help='Extract features and dump to YAML file.')
    parser.add_argument('--feature', action='append',
                        required=True,
                        choices=[PROJ, SENTIWS, REGSCORE, COUNT,
                                 PHRASES, POSF],
                        help='Specify which features to use.')
    parser.add_argument('--learner', action='append',
                        required=True,
                        choices=[LINSVC, RFC, ABC, GBC, ETC],
                        help='Specify which learners to use.')
    parser.add_argument('--skip-training', action="store_true",
                        help='Skips training. Useful with --save-vectors.')
    parser.add_argument('--classify-ptb-file',
                        help='Classify PTB file')
    parser.add_argument('--classify-projected',
                        help='Projection XML file for classify PTB file')
    parser.add_argument('--classify-out',
                        help='Output file for classified phrases.')
    parser.add_argument('--classify-as-test', action='store_true',
                        help='Treat CLASSIFY_PTB_FILE as test file containing'
                             + 'gold labels')
    parser.add_argument('--do-cv', action='store_true',
                        help='Perform 10-fold Cross-Validation on train set')
    parser.add_argument('--eval-csv',
                        help='Output file for CSV with evaluation measures.')
    parser.add_argument('--feature-weights-csv',
                        help='Output file for CSV with feature importances')
    args = parser.parse_args()
    logging.basicConfig(filename='ensemble.log', level=logging.DEBUG,
                        format='%(asctime)s:%(module)s:'
                        + '%(levelname)s:%(message)s')
    logger.info("Starting. Config: %s", args)
    e = EnsembleLearner(args.feature, args.gold, args.projected,
                        args.folds,
                        args.mzn_reg_alphabet, args.mzn_reg_model,
                        args.mzn_reg_args, args.sentiws_pos,
                        args.sentiws_neg, args.classify_ptb_file,
                        args.classify_projected,
                        args.classify_out, args.classify_as_test,
                        args.do_cv, args.eval_csv, args.feature_weights_csv,
                        args.learner)
    if args.save_vectors:
        e.save_data()
    if not args.skip_training:
        e.build_classifier()
    if args.do_cv or args.classify_as_test:
        e.write_eval_data()

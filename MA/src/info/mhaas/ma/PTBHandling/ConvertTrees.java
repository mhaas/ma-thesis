/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package info.mhaas.ma.PTBHandling;

import edu.stanford.nlp.ling.Label;
import edu.stanford.nlp.parser.lexparser.AbstractTreebankParserParams;
import edu.stanford.nlp.parser.lexparser.EnglishTreebankParserParams;
import edu.stanford.nlp.parser.lexparser.NegraPennTreebankParserParams;
import edu.stanford.nlp.parser.lexparser.TreeBinarizer;
import edu.stanford.nlp.sentiment.CollapseUnaryTransformer;
import edu.stanford.nlp.trees.MemoryTreebank;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.TreeTransformer;
import java.io.File;
import java.util.LinkedList;
import java.util.List;

/**
 *
 * Converts PTB Trees into binary collapsed trees.
 *
 * @author Michael Haas &lt;haas@cl.uni-heidelberg.de&lt;
 */
public class ConvertTrees {

    private static final String PSEUDO_LABEL = "2";

    public static void attachPseudoLabels(Tree tree) {
        if (tree.isLeaf()) {
            return;
        }
        for (Tree child : tree.children()) {
            attachPseudoLabels(child);
        }
        Label l = tree.label();
        l.setValue(PSEUDO_LABEL);
    }

    public static void fixGappyLabels(Tree tree) {
        if (tree.isLeaf()) {
            return;
        }
        for (Tree child : tree.children()) {
            fixGappyLabels(child);
        }
        Label l = tree.label();
        String lValue = l.value();
        lValue = lValue.replace(" ", "-");
        l.setValue(lValue);
    }

    public static Tree convertTree(Tree tree, AbstractTreebankParserParams params, boolean binarize, boolean collapseUnary, boolean pseudoLabel) {
        return convertTree(tree, params, binarize, collapseUnary, pseudoLabel, false);
    }

    public static Tree convertTree(Tree tree, AbstractTreebankParserParams params, boolean binarize, boolean collapseUnary, boolean pseudoLabel, boolean fixGappyLabels) {
        // Following is adapted from ./stanford-corenlp-full-2013-11-12/src/edu/stanford/nlp/pipeline/ParserAnnotator.java
        if (binarize) {
            TreeBinarizer binarizer = new TreeBinarizer(params.headFinder(), params.treebankLanguagePack(),
                    false, false, 0, false, false, 0.0, false, true, true);
            tree = binarizer.transformTree(tree);
        }
        if (collapseUnary) {
            TreeTransformer tf = new CollapseUnaryTransformer();
            tree = tree.transform(tf);
        }
        if (fixGappyLabels) {
            fixGappyLabels(tree);
        }
        if (pseudoLabel) {
            attachPseudoLabels(tree);
        }
        return tree;
    }

    public static List<Tree> loadTreesFromFileName(AbstractTreebankParserParams params, String fileName, boolean binarize, boolean collapseUnary, boolean pseudoLabel, boolean deepen, boolean fixGappyLabels) {
        return loadTreesFromFile(params, new File(fileName), binarize, collapseUnary, pseudoLabel, deepen, fixGappyLabels);
    }

    public static List<Tree> loadTreesFromFile(AbstractTreebankParserParams params, File file, boolean binarize, boolean collapseUnary, boolean pseudoLabel) {
        return loadTreesFromFile(params, file, binarize, collapseUnary, pseudoLabel, false, false);
    }

    public static List<Tree> loadTreesFromFile(AbstractTreebankParserParams params, File file, boolean binarize, boolean collapseUnary, boolean pseudoLabel, boolean deepen, boolean fixGappyLabels) {
        List<Tree> trees = new LinkedList<Tree>();
        // Uses PenntreeReader internally
        MemoryTreebank treebank = new MemoryTreebank();
        treebank.loadPath(file, null);
        DeepeningTreeTransformer deepener = new DeepeningTreeTransformer();
        for (Tree tree : treebank) {
            // Deepen before we remove the labels
            if (deepen) {
                tree = tree.transform(deepener);
            }
            tree = convertTree(tree, params, binarize, collapseUnary, pseudoLabel, fixGappyLabels);

            trees.add(tree);
        }
        return trees;
    }

    public static void main(String[] args) {
        if (args.length < 1) {
            System.err.println("Usage: First argument must be file to PTB");
            System.err.println("Optional: -binarize -collapseUnary -applyLabels -deepen -fixGappyLabels");
            System.exit(-1);
        }

        boolean binarize = false;
        boolean collapseUnary = false;
        boolean applyLabels = false;
        boolean german = false;
        boolean deepen = false;
        boolean fixGappyLabels = false;
        for (int i = 1; i < args.length; i++) {
            String a = args[i];
            if (a.equals("-binarize")) {
                binarize = true;
            } else if (a.equals("-collapseUnary")) {
                collapseUnary = true;
            } else if (a.equals("-applyLabels")) {
                applyLabels = true;
            } else if (a.equals("-german")) {
                german = true;
            } else if (a.equals("-deepen")) {
                deepen = true;
            } else if (a.equals("-fixGappyLabels")) {
                fixGappyLabels = true;
            } else {
                System.err.println("Invalid Argument: " + a);
                System.exit(-2);
            }
        }
        if (binarize && !applyLabels) {
            System.err.println("Requested binarization without application of pseudo labels");
            System.err.println("The resulting trees will not be binary on deserialization");
        }
        if (deepen && (!german)) {
            System.err.println("You requested PP deepening for English. This is untested.");
        }
        System.err.println("Binarizing trees: " + binarize);
        System.err.println("Collapsing unary nodes: " + collapseUnary);
        System.err.println("Applying pseudo labels: " + applyLabels);
        System.err.println("German: " + german);
        System.err.println("PP Deepening: " + deepen);
        System.err.println("Remove white space in node labels: " + fixGappyLabels);

        AbstractTreebankParserParams params = null;
        if (german) {
            params = new NegraPennTreebankParserParams();
        } else {
            params = new EnglishTreebankParserParams();
        }
        List<Tree> trees = loadTreesFromFileName(params, args[0], binarize, collapseUnary, applyLabels, deepen, fixGappyLabels);
        for (Tree t : trees) {
            if (binarize && (!TreeUtil.isBinarized(t))) {
                System.err.println("Tree is not binarized. Aborting");
                System.exit(-1);
            }
            if (collapseUnary && (!TreeUtil.isUnaryCollapsed(t))) {
                System.err.println("Tree does not have its unary nodes collapsed. Aborting.");
                System.exit(-1);
            }
            System.out.println(t);
        }

    }

    private static List<Tree> loadTreesFromFileName(AbstractTreebankParserParams params, String fileName, boolean binarize, boolean collapseUnary, boolean applyLabels) {
        return loadTreesFromFileName(params, fileName, binarize, collapseUnary, applyLabels, false, false);
    }
}

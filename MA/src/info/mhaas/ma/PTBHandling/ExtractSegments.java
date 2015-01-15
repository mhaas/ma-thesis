/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package info.mhaas.ma.PTBHandling;

import edu.stanford.nlp.trees.MemoryTreebank;
import edu.stanford.nlp.trees.Tree;
import java.io.IOException;
import java.io.PrintStream;
import java.util.HashSet;

/**
 *
 * Extracts segments from a parse tree.
 *
 * Given a parse tree, this class finds all sub trees and prints the
 * accompanying sentence fragment.
 *
 * We get duplicate items for trees that look like this: (S (VP (TO to) (VP (VB
 * read)))))). The leaf is printed three times. We will filter these in a later
 * step.
 *
 * @author Michael Haas &lt;haas@computerlinguist.org&gt;
 */
public class ExtractSegments {

    /**
     * Walks the tree and prints the leaf nodes for each sub tree separately.
     *
     *
     * @param input Tree whose subtrees are to be printed
     * @param out OutputStream to which results are printed
     */
    public static void extractSegments(Tree input, PrintStream out) {


        for (Tree subTree : input) {
            //System.err.println(subTree.value());
            ExtractSegments.printSubTree(subTree, out);
        }
    }

    /**
     * Walks the tree and prints segments for sub trees with given root values.
     *
     * This can be used to print all subtrees for a VP or NP subtree. Matching
     * subtrees are handed to @link{extractSegments(Tree, PrintStream)}.
     *
     *
     * @param input Tree whose subtrees are to be printed
     * @param out Outputstream to which results are printed
     * @param requiredLabels Labels such as NP, VP whose subtrees will be
     * printed
     */
    public static void extractFilteredSegments(Tree input, PrintStream out, HashSet<String> requiredLabels) {
        for (Tree subTree : input) {
            if (requiredLabels.contains(subTree.value())) {
                extractSegments(subTree, out);
            }

        }

    }

    /**
     * Prints all leaf nodes for a tree.
     *
     * @param input Tree whose leaf nodes are printed
     * @param out OutputStream to which results are printed.
     */
    private static void printSubTree(Tree input, PrintStream out) {
        for (Tree subTree : input) {
            if (subTree.isLeaf()) {
                // label also has the index
                // out.print(subTree.label());
                // out.print("--");
                out.print(subTree.value());
                //out.print("---");
                //out.print(subTree.hashCode());
                out.print(" ");
            }
        }
        out.println();
    }

    /**
     * Convenience method - prints @link{extractSegments(Tree, PrintStream)} to @link{System.out}.
     *
     * @param input Tree whose subtrees are to be printed
     */
    public static void extractSegments(Tree input) {
        ExtractSegments.extractSegments(input, System.out);
    }

    /**
     * Prints subtrees for tree file.
     *
     * Assumes tree are binary and have their unary nodes collapsed.
     * 
     * @param args First argument: file name containing PTB format trees.
     * @throws java.io.IOException
     */
    public static void main(String[] args) throws IOException {
        if (args.length < 1) {
            System.err.println("First argument must be file name containing PTB format trees.");
            System.exit(-1);
        }
        String fileName = args[0];
        MemoryTreebank treebank = new MemoryTreebank();
        treebank.loadPath(fileName, null);
        //HashSet<String> required = new HashSet<String>();
        //required.add("VP");
        //required.add("NP");

        for (Tree tree : treebank) {
            if (!TreeUtil.isBinarized(tree)) {
                System.err.println(tree);
                System.err.println("Tree is not binarized. Aborting");
                throw new IOException("Tree not binary");
            }
            if (!TreeUtil.isUnaryCollapsed(tree)) {
                System.err.println("Tree does not have its unary nodes collapsed. Aborting");
                throw new IOException("Tree with uncollapsed unary nodes");
            }
            extractSegments(tree, System.out);
            // extractFilteredSegments(tree, System.out, required);
        }
    }
}

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package info.mhaas.ma.PTBHandling;

import edu.stanford.nlp.trees.Tree;

/**
 *
 * @author Michael Haas &lt;haas@cl.uni-heidelberg.de&gt;
 */
public class TreeUtil {

    public static void printTree(Tree tree) {
        printTree(tree, "");
    }

    public static void printTree(Tree tree, String indent) {
        System.err.print(indent);
        System.err.println(tree.label());
        for (Tree st : tree.children()) {
            printTree(st, indent + "  ");
        }
    }

    public static boolean isBinarized(Tree tree) {
        if (tree.children().length > 2) {
            return false;
        }
        for (Tree subTree : tree) {
            if (subTree.children().length > 2) {
                return false;
            }
        }
        return true;
    }

    public static boolean isUnaryCollapsed(Tree tree) {
        if (!tree.isLeaf() && (!tree.isPreTerminal()) && tree.children().length == 1) {
            return false;
        }
        for (Tree subTree : tree) {
            if ((!subTree.isLeaf()) && (!subTree.isPreTerminal()) && subTree.children().length == 1) {
                // TODO: log properly?
                System.err.println("Subtree has single child:");
                System.err.println(subTree);
                System.err.println("--------");
                return false;
            }
        }
        return true;
    }
}

/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package info.mhaas.ma.Evaluation;

import edu.stanford.nlp.ling.Label;
import edu.stanford.nlp.trees.Tree;
import java.util.List;

/**
 *
 * @author Michael Haas &lt;haas@cl.uni-heidelberg.de&gt;
 */
public class CCEvaluator {

    public static int collapseFineGrained(Label label) {
        return collapseFineGrained(label.value());
    }

    public static int collapseFineGrained(String label) {
        if (label.equals("0") || label.equals("1")) {
            return 0;
        } else if (label.equals("2")) {
            return 1;
        } else if (label.equals("3") || label.equals("4")) {
            return 2;
        } else {
            throw new IllegalArgumentException("Label not OK!: " + label);
        }
    }

    private static boolean labelMatches(Tree gold, Tree predicted) {
        Label goldLabel = gold.label();
        Label predLabel = predicted.label();
        return collapseFineGrained(goldLabel) == collapseFineGrained(predLabel);

    }

    public static void evaluate(List<CCMatchObject> matches) {
        int skippedIdentical = 0;
        // total is total trees of interest
        int total = 0;
        int leftRightOK = 0;
        int leftRightParentOK = 0;
        for (CCMatchObject mo : matches) {

            // first check whether left and right subtree have differing node labels
            // If not, look at the next tree
            if (labelMatches(mo.getLeftGold(), mo.getRightGold())) {
                System.err.println("Left and Right gold share identical label. Not of interest, skipping!");
                skippedIdentical++;
                continue;
            }
            total++;
            boolean leftOK = labelMatches(mo.getLeftGold(), mo.getLeftPred());
            //System.err.println("Match " + leftOK + " for left subtree at " + mo.getTreeIndex());
            boolean rightOK = labelMatches(mo.getRightGold(), mo.getRightPred());
            //System.err.println("Match " + rightOK + " for right subtree at " + mo.getTreeIndex());
            boolean parentOK = labelMatches(mo.getParentGold(), mo.getParentPred());
            //System.err.println("Match " + parentOK + " for parent node at " + mo.getTreeIndex());

            if (leftOK && rightOK) {
                leftRightOK++;
            }
            if (leftOK && rightOK && parentOK) {
                leftRightParentOK++;
            }

        }
        System.err.println("Skipped identical left and right labels: " + skippedIdentical);
        System.err.println("Trees of interest: " + total);
        System.err.println("Left + Right correctly predicted: " + leftRightOK);
        System.err.println("Left + Right + Parent correctly predicted: " + leftRightParentOK);
        System.out.println("total;leftRight;leftRightParent;leftRightAcc;leftRightParentAcc;");
        System.out.print(total + ";" + leftRightOK + ";" + leftRightParentOK + ";");
        System.out.println((leftRightOK / (double) total) + ";" + (leftRightParentOK / (double) total) + ";");
    }

}

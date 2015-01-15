/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package info.mhaas.ma.PTBHandling;

import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.TreeTransformer;
import java.util.ArrayList;
import java.util.List;

/**
 * This class implements a TreeTransformer based on 
 * <p>
 * Samuelsson, Y., &amp; Volk, M. (2004).
 * Automatic node insertion for treebank deepening.
 * In Proceedings of the Third Workshop on Treebanks and Linguistic
 * Theories (TLT), Tübingen, Germany (pp. 127-136).
 * </p>
 * 
 * Only PPs are handled. Unary nodes are not inserted.
 * 
 * For reference,
 * the STTS tagset lists the following:
 * <ul>
 * <li>APPR    Präposition; Zirkumposition links       in [der Stadt], ohne [mich]</li>
 * <li>APPRART Präposition mit Artikel                 im [Haus], zur [Sache]</li>
 * <li>APPO    Postposition                            [ihm] zufolge, [der Sache] wegen</li>
 * <li>APZR    Zirkumposition rechts                   [von jetzt] an</li>
 * </ul>
 * 
 * @author Michael Haas &lt;haas@cl.uni-heidelberg.de&gt;
 */
public class DeepeningTreeTransformer implements TreeTransformer {

    private boolean checkSpanEquality(List<Tree> originalLeaves, List<Tree> newLeaves) {

        if (originalLeaves.size() != newLeaves.size()) {
            return false;
        }
        for (int i = 0; i < originalLeaves.size(); i++) {
            Tree origLeaf = originalLeaves.get(i);
            Tree newLeaf = newLeaves.get(i);
            if (!origLeaf.equals(newLeaf)) {
                return false;
            }

        }
        return true;

    }

    @Override
    public Tree transformTree(Tree t) {
        // TODO: do I have to copy the tree?
        if (t.isLeaf()) {
            return t;
        }


        // Algorithm is as follows:
        // anything before APPR and APPRART goes before the new NP child
        // anything after APPR and APPRART goes into NP child OR anything
        // before APPO goes into NP child
        // but anything we see after APZR and APPO goes to the left of the new
        // NP child
        if (t.value().equals("PP")) {
            Tree npTree = t.treeFactory().newTreeNode("NP", null);
            // APPR is inserted _before_ the new NP,
            // APZR and APPO inserted _after_ the new NP
            // This also handles APPR ADJ NN APZR case
            // "_von_ der Atmosphäre _her_"
            ArrayList<Tree> childrenLeftOfNP = new ArrayList<Tree>();
            ArrayList<Tree> childrenRightOfNP = new ArrayList<Tree>();

            Tree[] children = t.children();
            boolean seenPRStart = false;
            boolean seenPREnd = false;
            for (int index = 0; index < children.length; index++) {
                Tree curChild = children[index];
                if (curChild.value().equals("APZR")) {
                    seenPREnd = true;
                    seenPRStart = true;
                }
                if (curChild.value().equals("APPO")) {
                    seenPREnd = true;
                    // APPO is also the start of a preposition
                    // We need this to prevent the APPO from going
                    // left of the NP
                    seenPRStart = true;

                    if (npTree.isLeaf()) {
                        // APPO trick
                        // anything before APPO becomes the NP
                        // unless we already have something in the new NP tree
                        npTree.setChildren(childrenLeftOfNP);
                        childrenLeftOfNP.clear();
                    }
                }
                if (!seenPRStart) {
                    childrenLeftOfNP.add(curChild);
                } else if (seenPREnd) {
                    childrenRightOfNP.add(curChild);
                    // Do not use npTree.isempty() as the tree is not empty - it does have a label
                    // Test for isLeaf() instead.
                } else {
                    npTree.addChild(curChild);
                }

                if (curChild.value().equals("APPR") || curChild.value().equals("APPRART")) {
                    seenPRStart = true;
                }
            }

            ArrayList<Tree> newChildren = new ArrayList<Tree>();
            newChildren.addAll(childrenLeftOfNP);
            newChildren.add(npTree);
            newChildren.addAll(childrenRightOfNP);
            // now make sure that the new NP does not only contain
            // AP, AVP or CNP
            // TODO:
            // Implement this part:
            // "But if the CNP has siblings
            //(typically modifiers) that belong to the same NP, then it gets an NP mother."
            // Addition: Do not add NP on (PP (APPR bis) (ADV heute))
            // That, is we require an NN or NP inside the new NP
            boolean nounFound = false;
            List<Tree> npChildren = npTree.getChildrenAsList();
            for (Tree npChild : npChildren) {
                String val = npChild.value();
                // TODO: this is untested.
                if (val.equals("AP") || val.equals("AVP") || val.equals("CNP")) {
                    // return unmodified tree
                    return t;
                }
                // According to the negra page, there is no NN
                // http://www.coli.uni-saarland.de/projects/sfb378/negra-corpus/knoten.html
                if (val.equals("NP") || val.equals("MPN") || val.equals("NN")) {
                    nounFound = true;
                }
            }
            if (!nounFound) {
                return t;
            }

            // sanity checks: is leaf order still the same?
            // eg does the new tree yield the same span?
            List<Tree> originalLeaves = t.getLeaves();
            // insert new children
            t.setChildren(newChildren);
            // if spans are not equal, we never recover - just bail
            boolean spansEqual = this.checkSpanEquality(originalLeaves, t.getLeaves());
            if (!spansEqual) {
                throw new AssertionError("Spans not equal, programming mistake!");
            }


        }

        return t;
    }
}

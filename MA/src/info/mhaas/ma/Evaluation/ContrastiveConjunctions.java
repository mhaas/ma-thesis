/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package info.mhaas.ma.Evaluation;

import edu.stanford.nlp.trees.MemoryTreebank;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.Treebank;
import edu.stanford.nlp.trees.tregex.TregexMatcher;
import java.io.File;

import edu.stanford.nlp.trees.tregex.TregexPattern;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;

/**
 *
 * @author Michael Haas &lt;haas@cl.uni-heidelberg.de&gt;
 */
public class ContrastiveConjunctions {

    private final MemoryTreebank predicted;
    private final MemoryTreebank gold;
    private final MemoryTreebank parses;

    private final static String CSRE = "ROOT < (/S/=left) < (/S/=right !== =left < /,/ << /aber/ $,, =left)";
    private final static String CAPRE = "/CAP/=left < (/KON/ </aber/)  $++ /AP/=right";
    // Longer path, captures different trees where 'aber' sits deeper
    // Need to exclude one node containing NP as it's a false positive
    private final static String CAPRE2 = "/CAP/=left < (/CAP/ < (/KON/ </aber/)) $ (/(AP|ADJA)/=right !== /NP/)";

    private final HashSet<Integer> matchedTrees;

    private final List<CCMatchObject> matches;

    public ContrastiveConjunctions(File predicted, File gold, File parses) {

        // Must be MemoryTreebank because others do not support
        // List interface for get()
        this.predicted = new MemoryTreebank();
        this.predicted.loadPath(predicted, null);
        this.gold = new MemoryTreebank();
        this.gold.loadPath(gold, null);
        this.parses = new MemoryTreebank();
        this.parses.loadPath(parses, null);
        assert this.parses.size() == this.predicted.size();
        assert this.predicted.size() == this.gold.size();
        this.matchedTrees = new HashSet<>();
        this.matches = new ArrayList<>();

    }

    public void match() {
        TregexPattern csPat = TregexPattern.compile(CSRE);
        TregexPattern capPat = TregexPattern.compile(CAPRE);
        TregexPattern cap2Pat = TregexPattern.compile(CAPRE2);
        this.matchPattern(csPat);
        this.matchPattern(capPat);
        this.matchPattern(cap2Pat);

    }

    public void eval() {
        CCEvaluator.evaluate(this.matches);
    }

    public void matchPattern(TregexPattern pat) {

        System.err.println("matchPattern called: " + pat.pattern());
        int treesFound = 0;
        for (int i = 0; i < this.parses.size(); i++) {
            //System.out.println("Tree number " + i);
            Tree currentParse = this.parses.get(i);
            TregexMatcher matcher = pat.matcher(currentParse);

            if (!matcher.find()) {
                // no match here. let's try the next tree!
                continue;
            }
            if (this.matchedTrees.contains(i)) {
                System.err.println("Already seen tree, skipping: " + i);
                continue;
            } else {
                this.matchedTrees.add(i);
            }
            treesFound++;
            // Tree subTree = matcher.getMatch();
            // Cool, we got a match.
            // Let's get left and right trees.
            Tree left = matcher.getNode("left");
            Tree right = matcher.getNode("right");

            int leftIdx = left.nodeNumber(currentParse);
            int rightIdx = right.nodeNumber(currentParse);

            Tree currentPred = this.predicted.get(i);
            Tree currentGold = this.gold.get(i);

            CCMatchObject mo = new CCMatchObject(currentPred, currentGold,
                    currentParse, i, leftIdx, rightIdx);
            this.matches.add(mo);

        }
        System.err.println("Matched " + treesFound + " trees.");

    }

    public static void main(String[] args) {

        File parses = new File(args[0]);
        File gold = new File(args[1]);
        File predicted = new File(args[2]);

        ContrastiveConjunctions cc = new ContrastiveConjunctions(predicted, gold, parses);

        cc.match();
        cc.eval();
    }

}

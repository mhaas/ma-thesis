/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package info.mhaas.ma.PTBHandling;

import edu.stanford.nlp.parser.lexparser.AbstractTreebankParserParams;
import edu.stanford.nlp.parser.lexparser.EnglishTreebankParserParams;
import edu.stanford.nlp.trees.MemoryTreebank;
import edu.stanford.nlp.trees.Tree;
import java.io.File;
import java.io.StringReader;
import java.net.URL;
import java.util.List;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import static org.junit.Assert.*;

/**
 *
 * @author Michael Haas <haas@computerlinguist.org>
 */
public class ConvertTreesTest {

    private Tree originalTree;
    private Tree pseudoLabeledTree;
    private static final String tt = "(S\n"
            + "  (NP (DT this) (JJ particular) (NN thief))\n"
            + "  (VP (VBZ is)\n"
            + "    (ADJP (RB very) (JJ unusual)))\n"
            + "  (. .))";
    private static final String pseudoLabeled = "(2\n"
            + "  (2 (2 this) (2 particular) (2 thief))\n"
            + "  (2 (2 is)\n"
            + "    (2 (2 very) (2 unusual)))\n"
            + "  (2 .))";
    private AbstractTreebankParserParams params;

    public ConvertTreesTest() {
        this.params = new EnglishTreebankParserParams();
    }

    @Before
    public void setUp() {
        MemoryTreebank treebank = new MemoryTreebank();
        StringReader r = new StringReader(tt);
        treebank.load(r);
        this.originalTree = treebank.get(0);
        treebank.clear();
        r = new StringReader(pseudoLabeled);
        treebank.load(r);
        this.pseudoLabeledTree = treebank.get(0);
    }

    @After
    public void tearDown() {
    }

    /**
     * Test of attachPseudoLabels method, of class ConvertTrees.
     */
    @Test
    public void testAttachPseudoLabels() {
        //System.out.println("attachPseudoLabels");
        // TODO: is also tested below
        // Do not deep-copy here because we want the tree to be modified in-place
        ConvertTrees.attachPseudoLabels(this.originalTree);
        assertEquals(this.originalTree, this.pseudoLabeledTree);
        // TODO review the generated test code and remove the default call to fail.
    }

    /**
     * Test of convertTree method, of class ConvertTrees.
     */
    @Test
    public void testConvertTree() {
        System.out.println("convertTree");
        boolean binarize = false;
        boolean collapseUnary = false;
        boolean pseudoLabel = false;

        Tree result = ConvertTrees.convertTree(this.originalTree.deepCopy(), params, binarize, collapseUnary, pseudoLabel);
        assertEquals(result, this.originalTree);

        binarize = true;
        result = ConvertTrees.convertTree(this.originalTree.deepCopy(), params, binarize, collapseUnary, pseudoLabel);
        assert (TreeUtil.isBinarized(result));
        binarize = false;
        collapseUnary = true;
        result = ConvertTrees.convertTree(this.originalTree.deepCopy(), params, binarize, collapseUnary, pseudoLabel);
        assert (TreeUtil.isUnaryCollapsed(result));
        binarize = true;
        result = ConvertTrees.convertTree(this.originalTree.deepCopy(), params, binarize, collapseUnary, pseudoLabel);
        assert (TreeUtil.isBinarized(result) && TreeUtil.isUnaryCollapsed(result));
        binarize = false;
        collapseUnary = false;
        pseudoLabel = true;
        result = ConvertTrees.convertTree(this.originalTree.deepCopy(), params, binarize, collapseUnary, pseudoLabel);
        assertEquals(result, this.pseudoLabeledTree);
        binarize = true;
        collapseUnary = true;
        result = ConvertTrees.convertTree(this.originalTree.deepCopy(), this.params, binarize, collapseUnary, pseudoLabel);
        assert (TreeUtil.isBinarized(result) && TreeUtil.isUnaryCollapsed(result));
        // TODO: test pseudo label

    }

    @Test
    public void testIsSerializedTreeBinary() {
        //It seems to me that TreeBinarizer modifies the labels in a way which
        //causes the TreeBank parsing code to insert additional nodes on
        //de-serializing the parse trees. It basically stores some data on the
        //original markup in the labels, from what I have seen.
        //
        //I have not verified this by reading the source, but from my
        //experiments, it is sufficient to change the labels as done in
        //BuildBinarizedDataset::setUnknownLabels.

        boolean binarize = true;
        boolean collapseUnary = false;
        boolean pseudoLabel = false;

        Tree result = ConvertTrees.convertTree(this.originalTree.deepCopy(), params, binarize, collapseUnary, pseudoLabel);
        result = serializeAndDeSerialize(result);
        // this apparently is the desired behaviour
        assertFalse(TreeUtil.isBinarized(result));// && TreeUtil.isUnaryCollapsed(result));

        pseudoLabel = true;
        result = ConvertTrees.convertTree(this.originalTree.deepCopy(), params, binarize, collapseUnary, pseudoLabel);
        result = serializeAndDeSerialize(result);
        assert (TreeUtil.isBinarized(result)); //&& TreeUtil.isUnaryCollapsed(result));

    }

    /**
     * Test of loadTreesFromFile method, of class ConvertTrees.
     */
    @Test
    public void testLoadTreesFromFile() {
        System.out.println("loadTreesFromFile");

        URL url = this.getClass().getResource("trees.txt");

        File testTrees = new File(url.getFile());

        boolean binarize = true;
        boolean collapseUnary = true;
        boolean pseudoLabel = false;
        List<Tree> result = ConvertTrees.loadTreesFromFile(this.params, testTrees, binarize, collapseUnary, pseudoLabel);
        assert (result.size() > 0);
        for (Tree t : result) {
            assert (TreeUtil.isBinarized(t) && TreeUtil.isUnaryCollapsed(t));
        }
    }

    private static Tree serializeAndDeSerialize(Tree t) {
        MemoryTreebank treebank = new MemoryTreebank();
        StringReader r = new StringReader(t.toString());
        treebank.load(r);
        Tree deSerializedTree = treebank.get(0);
        return deSerializedTree;

    }
}

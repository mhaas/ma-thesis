/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package info.mhaas.ma.Evaluation;

import edu.stanford.nlp.trees.Tree;

/**
 *
 *
 * @author Michael Haas &lt;haas@cl.uni-heidelberg.de&gt;
 */
public class CCMatchObject {

    private Tree predTree;
    private Tree goldTree;
    private Tree parseTree;
    private int treeIndex;
    private int leftIdx;
    private int rightIdx;

    public CCMatchObject(Tree predTree, Tree goldTree, Tree parseTree, int treeIndex, int leftIdx, int rightIdx) {
        this.predTree = predTree;
        this.goldTree = goldTree;
        this.parseTree = parseTree;
        this.treeIndex = treeIndex;
        this.leftIdx = leftIdx;
        this.rightIdx = rightIdx;
    }

    public Tree getLeftPred() {
        return this.predTree.getNodeNumber(this.getLeftIdx());
    }

    public Tree getLeftGold() {
        return this.goldTree.getNodeNumber(this.getLeftIdx());
    }

    public Tree getRightPred() {
        return this.predTree.getNodeNumber(this.getRightIdx());
    }

    public Tree getRightGold() {
        return this.goldTree.getNodeNumber(this.getRightIdx());
    }

    /**
     * Get the common parent of left and right node.
     *
     * The underlying assumption is that left and right are immediate siblings
     * in a binary tree.
     *
     * @return
     */
    public Tree getParentGold() {
        return this.getParentNode(this.goldTree);
    }

    /**
     * Get the common parent of left and right node.
     *
     * The underlying assumption is that left and right are immediate siblings
     * in a binary tree.
     *
     * @return
     */
    public Tree getParentPred() {
        return this.getParentNode(this.predTree);
    }

    private Tree getParentNode(Tree someTree) {
        // parent() method requires tree root to be passed in.
        // Calling parent() w/o this will return null.
        Tree leftParent = someTree.getNodeNumber(this.getLeftIdx()).parent(someTree);
        Tree rightParent = someTree.getNodeNumber(this.getRightIdx()).parent(someTree);
        assert leftParent == rightParent;
        assert leftParent != null;
        return leftParent;
    }

    /**
     * @return the treeIndex
     */
    public int getTreeIndex() {
        return treeIndex;
    }

    /**
     * @return the leftIdx
     */
    public int getLeftIdx() {
        return leftIdx;
    }

    /**
     * @return the rightIdx
     */
    public int getRightIdx() {
        return rightIdx;
    }

}

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package info.mhaas.ma.Annotation;

import edu.stanford.nlp.ling.Label;
import edu.stanford.nlp.trees.MemoryTreebank;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.Treebank;
import info.mhaas.ma.PTBHandling.TreeUtil;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Set;

/**
 *
 * Go from manually annotated fragments back to PTB parse trees.
 *
 * Annotation is done on a fragment-level. For evaluation purposes, the
 * per-fragment annotation need to be applied to the original parse tree.
 *
 * This class takes the annotated fragments and the parse trees and outputs
 * parse trees with the gold standard annotated.
 *
 * @author Michael Haas &lt;haas@cl.uni-heidelberg.de&gt;
 */
public class AnnotationToPTB {

    private static String extractSubtreeFragment(Tree t) {
        StringBuilder sb = new StringBuilder();
        for (Tree subTree : t) {
            if (subTree.isLeaf()) {
                // label also has the index
                // out.print(subTree.label());
                // out.print("--");
                sb.append(subTree.value());
                //out.print("---");
                //out.print(subTree.hashCode());
                sb.append(" ");
            }
        }
        return sb.toString().trim();
    }

    private static HashMap<String, Integer> loadAnnotatedFragments(String fileName) throws IOException {

        HashMap<String, Integer> result = new HashMap<String, Integer>();

        BufferedReader r = new BufferedReader(new FileReader(new File(fileName)));
        String line;
        while ((line = r.readLine()) != null) {
            String[] split = line.split("\t");
            if (split[0].equals("0")) {
                System.err.println("Line is 0, skipping!");
                continue;
            }
            System.out.println(line);
            if (split.length < 2) {
                throw new IOException("Sorry, Invalid file format.");
            } else {
                // strings need to be enclosed in "
                assert split[0].startsWith("\"");
                if ("".equals(split[0])) {
                    System.err.println("Segment is empty string, skipping!");
                    continue;
                }
                if ( (! split[0].contains("\"")) || split[0].length() < 2) {
                    System.err.println("Segment is empty, skipping!");
                    continue;
                } 
                split[0] = split[0].substring(1, split[0].length() - 1);
            }

            // TODO: check for duplicates!
            String key = split[0].trim();
            // Un-quote quoted double quotes
            key = key.replace("\"\"", "\"");
            Integer value = Integer.decode(split[1]);
            if (result.containsKey(key)) {
                System.err.println("Fragment map already contains key " + key);
                System.err.println("Current value: " + result.get(key));
                System.err.println("New value: " + value);
            }
            result.put(key, value);

        }
        r.close();
        return result;

    }

    public static Treebank backToTrees(String annotatedFragmentsFile, String ptbFile) throws IOException {
        MemoryTreebank treebank = new MemoryTreebank();
        treebank.loadPath(ptbFile, null);
        HashMap<String, Integer> gold = loadAnnotatedFragments(annotatedFragmentsFile);
        Set<String> seenFragments = new HashSet<String>();

        for (Tree t : treebank) {
            // The entire pipeline assumes that trees are binarized

            if (!TreeUtil.isBinarized(t)) {
                System.err.println("Tree is not binarized. Aborting");
                throw new IOException("Tree not binary");
            }
            if (!TreeUtil.isUnaryCollapsed(t)) {
                System.err.println("Tree does not have its unary nodes collapsed. Aborting");
                throw new IOException("Tree with uncollapsed unary nodes");
            }
            for (Tree subTree : t) {
                if (subTree.isLeaf()) {
                    continue;
                }
                String fragment = extractSubtreeFragment(subTree);
                // look up fragment in gold standard
                Integer label = 2;
                if (!gold.containsKey(fragment)) {
                    System.err.println("Could not find fragment in gold: >>" + fragment + "<<");
                    System.err.println("Defaulting to 2");

                } else {
                    label = gold.get(fragment);
                }
                Label nodeLabel = subTree.label();
                nodeLabel.setValue(label.toString());
                seenFragments.add(fragment);

            }
        }
        // some sanity checks
        for (String annotatedFragment : gold.keySet()) {
            if (!seenFragments.contains(annotatedFragment)) {
                System.err.println("Annotated Fragments contains a fragment we did not see in the PTB file");
                System.err.println(annotatedFragment);
            }
        }
        return treebank;
    }

    public static void main(String args[]) throws IOException {
        if (args.length < 3) {
            System.err.println("First argument: annotated fragments file");
            System.err.println("Second argument: PTB file");
            System.err.println("Third argument: output file");
            System.exit(-1);
        }
        Treebank tBank = backToTrees(args[0], args[1]);
        BufferedWriter out = new BufferedWriter(new FileWriter(args[2]));
        for (Tree t : tBank) {
            //System.out.println(t);
            out.write(t.toString());
            out.write("\n");
        }
        out.close();
    }
}

/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package info.mhaas.ma.PTBHandling;

import edu.stanford.nlp.trees.MemoryTreebank;
import java.io.StringReader;
import edu.stanford.nlp.trees.Tree;
import org.junit.After;
import org.junit.AfterClass;
import org.junit.Before;
import org.junit.BeforeClass;
import org.junit.Test;
import static org.junit.Assert.*;

/**
 *
 * @author haas
 */
public class DeepeningTreeTransformerTest {

    public DeepeningTreeTransformerTest() {
    }

    @BeforeClass
    public static void setUpClass() throws Exception {
    }

    @AfterClass
    public static void tearDownClass() throws Exception {
    }

    @Before
    public void setUp() {
    }

    @After
    public void tearDown() {
    }

    private void testHelper(String inputTree, String desiredTree) {

        MemoryTreebank treebank = new MemoryTreebank();
        StringReader r = new StringReader(inputTree);
        treebank.load(r);
        Tree tree = treebank.get(0);
        treebank.clear();

        r = new StringReader(desiredTree);
        treebank.load(r);
        Tree expectedTree = treebank.get(0);
        treebank.clear();

        DeepeningTreeTransformer instance = new DeepeningTreeTransformer();
        Tree result = tree.transform(instance);
        assertEquals(expectedTree, result);

    }

    /**
     * Test of transformTree method, of class DeepeningTreeTransformer.
     */
    @Test
    public void testAPPR() {

        String input = "(CS (S (NP-SB (ART Eine) (ADJA skrupellose) (NN Verbrecherbande)) (VVFIN legt) (PRF-OA sich) (ADV unwissentlich) (PP (APPR mit) (ART einem) (ADJA psychopathischen) (NN Serienmörder)) (PTKVZ an)) ($*LRB* -) (S (PDS das) (VMFIN kann) (ADV ja) (ADV nur) (VP (PP (APPR in) (ART einem) (NN Blutbad)) (VVINF enden))) ($. .))";
        String expected = "(CS (S (NP-SB (ART Eine) (ADJA skrupellose) (NN Verbrecherbande)) (VVFIN legt) (PRF-OA sich) (ADV unwissentlich) (PP (APPR mit) (NP (ART einem) (ADJA psychopathischen) (NN Serienmörder))) (PTKVZ an)) ($*LRB* -) (S (PDS das) (VMFIN kann) (ADV ja) (ADV nur) (VP (PP (APPR in) (NP (ART einem) (NN Blutbad))) (VVINF enden))) ($. .))";
        this.testHelper(input, expected);

    }

    @Test
    public void testAPPO() {
        String input = "(S (AP (AVP (S (KOUS Als) (VAFIN hätte) (PIS-SB man) (VP (PRF-OA sich)))) (PP (ART einen) (NN Abend) (APPO lang)) (ADJD wahllos)) (PP (APPR durch) (ADJA obskure) (NN YouTube-Videos)) (VVFIN geklickt) ($. .))";
        String expected = "(S (AP (AVP (S (KOUS Als) (VAFIN hätte) (PIS-SB man) (VP (PRF-OA sich)))) (PP (NP (ART einen) (NN Abend)) (APPO lang)) (ADJD wahllos)) (PP (APPR durch) (NP (ADJA obskure) (NN YouTube-Videos))) (VVFIN geklickt) ($. .))";
        this.testHelper(input, expected);
    }

    @Test
    public void testAPZR() {

        String input = "(S (KON Aber) (PP (APPR von) (ART der) (NN Atmosphäre) (APZR her)) (VVFIN gehört) (NP-SB (ART der) (ADJA australische) (NN Film)) (ADJD definitiv) (PP (APPR zu) (ART den) (ADJA besseren) (NN Found-Footage-Streifen) (NP (ART der) (ADJA letzten) (NN Zeit))) ($. .))";
        // NP after APP* goes into PP
        String expected = "(S (KON Aber) (PP (APPR von) (NP (ART der) (NN Atmosphäre)) (APZR her)) (VVFIN gehört) (NP-SB (ART der) (ADJA australische) (NN Film)) (ADJD definitiv) (PP (APPR zu)  (NP (ART den) (ADJA besseren) (NN Found-Footage-Streifen) (NP (ART der) (ADJA letzten) (NN Zeit)))) ($. .))";
        //String expected = "(S (KON Aber) (PP (APPR von) (NP (ART der) (NN Atmosphäre)) (APZR her)) (VVFIN gehört) (NP-SB (ART der) (ADJA australische) (NN Film)) (ADJD definitiv) (PP (APPR zu)  (NP (ART den) (ADJA besseren) (NN Found-Footage-Streifen)) (NP (ART der) (ADJA letzten) (NN Zeit))) ($. .))";
        
        this.testHelper(input, expected);
    }
    
    @Test
    public void testAPPRART() {
        String input = "(S (ADV Vielleicht) (VVFIN empfiehlt) (PRF-OA sich) (PP (APPR bei) (ART einer) (ADJA erneuten) (NN Sichtung) (NP (ART das) (ADJA frühzeitige) (NN Abschalten))) ($, ,) (S (KOUS wenn) (PPER-SB es) (PP (APPRART zur) (ADJA öden) (NN Phase)) (VVFIN kommt)) ($. .))";
        String expected = "(S (ADV Vielleicht) (VVFIN empfiehlt) (PRF-OA sich) (PP (APPR bei) (NP (ART einer) (ADJA erneuten) (NN Sichtung) (NP (ART das) (ADJA frühzeitige) (NN Abschalten)))) ($, ,) (S (KOUS wenn) (PPER-SB es) (PP (APPRART zur) (NP (ADJA öden) (NN Phase))) (VVFIN kommt)) ($. .))";
        this.testHelper(input, expected);
    }
    
    @Test
    public void testNPBeforeAPPR() {
        String input = "(PP (NP (BLAH fünf) (NN Meter)) (APPR vor) (ART dem) (NN Tor))";
        String expected = "(PP (NP (BLAH fünf) (NN Meter)) (APPR vor) (NP (ART dem) (NN Tor) ))";
        this.testHelper(input, expected);
    }
    
    /**
     * A tree which did not give correct results.
     * out-113.eps
     */
    @Test
    public void test1() {
        String input = "(NP (NN Durchaus) (PP (ADV sehenswert) (APPR mit) (ART ein) (PIDAT paar) (ADJA moralischen) (NN Ansätzen)) ($, ,) (S (PRELS-SB die) (ADV aber) (VP (AP (PTKNEG nicht) (PTKA allzu) (ADJD ernst)) (VZ (PTKZU zu) (VVINF nehmen))) (VAFIN sind)) ($. .))";
        String expected = "(NP (NN Durchaus) (PP (ADV sehenswert) (APPR mit) (NP (ART ein) (PIDAT paar) (ADJA moralischen) (NN Ansätzen))) ($, ,) (S (PRELS-SB die) (ADV aber) (VP (AP (PTKNEG nicht) (PTKA allzu) (ADJD ernst)) (VZ (PTKZU zu) (VVINF nehmen))) (VAFIN sind)) ($. .))";
        this.testHelper(input, expected);
                
        
    }
    
    // out-78.eps
    @Test
    public void test2() {
        String input = "(CS (S (PDS-OA Das) (ADV allein) (VVFIN spricht) (ADV schon) (PROAV dafür) ($, ,) (S (KOUS dass) (PIS-SB jeder) (PP (ADJD voll) (APPR bei) (ART der) (NN Sache)) (VAFIN war))) (KON und) (S (NP-SB (AP (ADV somit) (PIAT etwas)) (NN Gelungenes)) (VP (VVPP produziert) (VAINF werden)) (VMFIN konnte)) ($. .))";
        String expected = "(CS (S (PDS-OA Das) (ADV allein) (VVFIN spricht) (ADV schon) (PROAV dafür) ($, ,) (S (KOUS dass) (PIS-SB jeder) (PP (ADJD voll) (APPR bei) (NP (ART der) (NN Sache))) (VAFIN war))) (KON und) (S (NP-SB (AP (ADV somit) (PIAT etwas)) (NN Gelungenes)) (VP (VVPP produziert) (VAINF werden)) (VMFIN konnte)) ($. .))";
        this.testHelper(input, expected);    
    
    }
    
    // out-15.eps
    // This also tests (PP (APPR bis) (ADV heute))
    @Test
    public void test3() {
        String input = "(CS (S (NP-SB (ART Die) (AP (ADJD stark) (ADJA konzentrierte)) (NN Biografie) (NP (ART der) (ADJA politischen) (NN Denkerin))) (VVFIN stellt) (NP (ADV aber) (NN Fragen) ($, ,) (S (PRELS-SB die) (PP (APPR bis) (ADV heute)) (CAP (ADJD spannend) (KON und) (ADJD relevant)) (VAFIN sind)))) ($, ,) (KON und) (S (VAFIN ist) (VP (VP (PP (PTKNEG nicht) (ADV zuletzt) (APPR dank) (ART einer) (ADJA brillanten) (NN Hauptdarstellerin)) (ADJD wirklich) (VVPP sehenswert)) (VAPP geworden))) ($. .))";
        String expected = "(CS (S (NP-SB (ART Die) (AP (ADJD stark) (ADJA konzentrierte)) (NN Biografie) (NP (ART der) (ADJA politischen) (NN Denkerin))) (VVFIN stellt) (NP (ADV aber) (NN Fragen) ($, ,) (S (PRELS-SB die) (PP (APPR bis) (ADV heute)) (CAP (ADJD spannend) (KON und) (ADJD relevant)) (VAFIN sind)))) ($, ,) (KON und) (S (VAFIN ist) (VP (VP (PP (PTKNEG nicht) (ADV zuletzt) (APPR dank) (NP (ART einer) (ADJA brillanten) (NN Hauptdarstellerin))) (ADJD wirklich) (VVPP sehenswert)) (VAPP geworden))) ($. .))";
        this.testHelper(input, expected);

        
    }
 }

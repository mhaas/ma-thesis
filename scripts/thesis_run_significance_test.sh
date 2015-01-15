#!/bin/bash
set -e

source `dirname $0`/common.sh



function marker() {
    echo "=========="
}

function test_against_rntn() {
    echo "Testing: HeiST RNTN versus $2"
    $CODEDIR/scripts/thesis_significance_test.sh \
        $SPLITS \
        ${SPLITS}.rntn \
        $DATADIR/$1
marker
}

function test_against() {
    echo "Testing: $1 versus $2"
    $CODEDIR/scripts/thesis_significance_test.sh \
        $SPLITS \
        $DATADIR/$3 \
        $DATADIR/$4
marker
}
BASE=/film-rezensionen.de/

# Batantly token from naacl_compile_evaluation.sh

function main() {

    test_against_rntn lexicon_based/mznlasso_noshift/ 'MZN Lasso (No Shift)'
    # Now do some inter-method comparisons
    test_against 'RNTN Clusters' \
        'RNTN Clusters Partitioned' \
        $BASE/thesis-MZN-CLUSTER-C5000-OPT/german_sentiment_treebank_592_beta_splits.affordable_useful_35182.txt-c5000-p1.out.clusters_over_10_16sb.rntn \
        $BASE/thesis-MZN-CLUSTER-C5000-OPT/german_sentiment_treebank_592_beta_splits.affordable_useful_35182.txt-c5000-p1.out.clusters_over_0_9sb.rntn
    test_against 'Uptrain (HeiST x23) Clusters' \
        'Uptrain (HeiST x23) Clusters Partitioned' \
        $BASE/thesis-UPTRAIN_GST_CLUSTER_885/german_sentiment_treebank_592_beta_splits.affordable_useful_35182.txt-c5000-p1.out.vanilla_GST_WEIGHT_23.numHid_25_batchSize_22.clusters_over_10_16sb.rntn/ \
        $BASE/thesis-UPTRAIN_GST_CLUSTER_885_DIV/affordable_useful_35182.txt-c5000-p1.out.ensemble.clusters_over_0_8sb.numHid_25_batchSize_22/

    # Now compare against RNTN
    test_against_rntn lexicon_based/sentiws_noshift/ 'SentiWS (No Shift)'
    test_against_rntn $BASE/thesis-final-gst-proj-runs/projected-12/folds/ \
      'Projection' 
    test_against_rntn $BASE/thesis-MZN-CLUSTER-C5000-OPT/german_sentiment_treebank_592_beta_splits.affordable_useful_35182.txt-c5000-p1.out.clusters_over_10_16sb.rntn \
        'RNTN Clusters'
    test_against_rntn $BASE/thesis-MZN-CLUSTER-C5000-OPT/german_sentiment_treebank_592_beta_splits.affordable_useful_35182.txt-c5000-p1.out.clusters_over_0_9sb.rntn \
        'RNTN Clusters Partitioned'
    test_against_rntn $BASE/thesis-UPTRAIN_GST_885/vanilla_GST_WEIGHT_23.numHid_25_batchSize_22.rntn \
        'Uptrain (HeiST x23)'
    test_against_rntn $BASE/thesis-UPTRAIN_GST_CLUSTER_885/german_sentiment_treebank_592_beta_splits.affordable_useful_35182.txt-c5000-p1.out.vanilla_GST_WEIGHT_23.numHid_25_batchSize_22.clusters_over_10_16sb.rntn/ \
        'Uptrain (HeiST x23) Clusters'
    test_against_rntn $BASE/thesis-UPTRAIN_GST_CLUSTER_885_DIV/affordable_useful_35182.txt-c5000-p1.out.ensemble.clusters_over_0_8sb.numHid_25_batchSize_22/ \
        'Uptrain (HeiST x23) Clusters Partitioned'
    test_against_rntn $BASE/thesis-final-ensemble-gst/thesis-final-ensemble-gst-top1/ \
       'Ensemble'

}
main

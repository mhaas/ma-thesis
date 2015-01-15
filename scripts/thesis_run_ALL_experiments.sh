#!/bin/bash

source `dirname $0`/common.sh

set -e
$CODEDIR/scripts/thesis_run_sentiws_gst_eval.sh
$CODEDIR/scripts/thesis_run_projection.sh 
$CODEDIR/scripts/thesis_run_ensemble.sh 
$CODEDIR/scripts/thesis_run_train_rntn_gst.sh 
$CODEDIR/scripts/thesis_run_best_test_data_set_size.sh train
$CODEDIR/scripts/thesis_run_best_test_data_set_size.sh test
$CODEDIR/scripts/thesis_run_train_mzn_c5000_clusters.sh
$CODEDIR/scripts/thesis_run_train_mzn_c1000_clusters.sh 
$CODEDIR/scripts/thesis_run_train_tueba_clusters.sh 
$CODEDIR/scripts/thesis_run_train_clusters_divided.sh
# You will likely need this one:
# thesis_run_ensemble_for_uptrain-885.sh
$CODEDIR/scripts/thesis_run_uptrain_885.sh 
$CODEDIR/scripts/thesis_run_uptrain_885_clusters.sh 
$CODEDIR/scripts/thesis_run_uptrain_885_clusters_divided.sh 


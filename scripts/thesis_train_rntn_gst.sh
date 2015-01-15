#!/bin/bash

# get CLASSPATH
source `dirname $0`/train_common.sh

NUM_HID="25"
BATCH_SIZE="22"
train $1 $2 $3

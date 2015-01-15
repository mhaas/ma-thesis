#!/bin/bash

export MAJAVA=$CODEDIR/MA/
input=$1
out=`mktemp`
java -cp $MAJAVA/dist/MA.jar info.mhaas.ma.PTBHandling.ExtractSegments "$input" > $out
sort -u $out | wc -l
rm $out
                

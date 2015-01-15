#!/bin/bash

if [[ -z "$DATADIR" ]]; then
    echo "DATADIR variable is not set! Bye."
    exit 1
fi

echo "Extracting Stanford JAR files"

cd $DATADIR/3rdparty/
unzip stanford-corenlp-full-2014-01-04.zip

cd $OLDPWD
mkdir -p lib
cp $DATADIR/3rdparty/stanford-corenlp-full-2014-01-04/*jar lib/
cp $DATADIR/3rdparty/*jar lib/


ant -Dlibs.junit_4.classpath=lib/junit-4.12.jar:lib/hamcrest-core-1.3.jar $@


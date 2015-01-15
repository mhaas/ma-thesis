# Google Translate Interface #

This module reads text from a data source and translate it
using the Google Translate API.

## API KEY ##
Create a file secret.py and put KEY={yourkey} inside.

## Data Sources ##

### Text file ###
Text is read from a text file and translated line by line.

### Stanford Sentiment Treebank 1.0 ###
Text is read from the datasetSentences.txt file from stanfordSentimentTreebank.zip and translated line by line.

Each line contains a sentence. The sentence index is reproduced in the output file.



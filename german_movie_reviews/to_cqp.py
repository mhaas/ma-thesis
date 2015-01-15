#!/usr/bin/python
# -*- coding: utf-8 -*-

# This script converts downloaded movie reviews
# to the CQP vertical format.

import nltk
import os
import glob
import sys
import subprocess
import StringIO
import argparse


sent_tokenizer=nltk.data.load('tokenizers/punkt/german.pickle')
#tokenizer = nltk.tokenize.TreebankWordTokenizer()

TOKENIZER="/home/mitarb/versley/sources/cdec-2013-07-13/corpus/tokenize-anything.sh"

def sentence_split(text):
    """Given a text, this returns a list of all sentences."""
    sentences = sent_tokenizer.tokenize(text)
    return sentences
        
def tokenize_sentence(sentence):
    """Given a single sentence, this returns a list of tokens."""
    #tokens = tokenizer.tokenize(sentence)
    buf = StringIO.StringIO(sentence)
    handle = subprocess.Popen(TOKENIZER, stdin=subprocess.PIPE, stdout=subprocess.PIPE); 
    handle.stdin.write(sentence.encode("utf-8"))
    # send EOF
    handle.stdin.close()
    tokenized = handle.stdout.read()
    handle.poll()
    tokenized = tokenized.decode("utf-8")
    
    return tokenized.split(" ")

def temp_clean(text):
    """Change some tokens.

    The tokenizer is happier if it does not encounter --.
    Otherwise, it will consider that an invidual token, making
    it harder to convert the markers back to HTML tags later one.
    """ 
    text = text.replace("--EM-REPLACEMENT--", "EM-REPLACEMENT ")
    text = text.replace("--EM-REPLACEMENT-END--", " EM-REPLACEMENT-END")
    text = text.replace("--STRONG-REPLACEMENT--", "STRONG-REPLACEMENT ")
    text = text.replace("--STRONG-REPLACEMENT-END--", " STRONG-REPLACEMENT-END")
    return text


def back_to_html(text):
    """Convert markers back to HTML.

    temp_clean() should be run beforehand on 'text'.
    """
    # replacement order is important
    text = text.replace("EM-REPLACEMENT-END", "</em>")
    text = text.replace("EM-REPLACEMENT", "<em>")
    text = text.replace("STRONG-REPLACEMENT-END", "</strong>")
    text = text.replace("STRONG-REPLACEMENT", "<strong>")
    return text

def main(inputFile, skipSplitting):
    """Converts files to CQP vertical format.

    The 'inputFile' argument must be a string pointing to a directory
    or to a file. The output file will have '.cqp' appended to its
    name.
    """
    files = [inputFile]
    if os.path.isdir(inputFile):
        files = glob.glob(os.path.join(inputFile, "*.txt"))
    for f in files:
        print "Processing file %s" % f
        outFile = open(f + ".cqp", "w")
        fileName = os.path.basename(f)
        outFile.write('<text id="filmberichte/%s">\n' % fileName)
        fh = open(f, "r")
        # clean up the replacements for <em> and <strong> so they do not get tokenized
        if skipSplitting:
            sentences = fh.readlines()
            sentences = map(lambda x: x.decode("utf-8"), sentences)
        else:
            text = temp_clean(fh.read().decode("utf-8"))
            sentences = sentence_split(text)
        for sentence in sentences:
            outFile.write("<s>\n")
            for token in tokenize_sentence(sentence):
                 # add <em> and <strong> back
                outFile.write(back_to_html(token).encode("utf-8"))
                outFile.write("\n")
            outFile.write("</s>\n")
        outFile.write('</text>')
        outFile.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Transform text files into CQP vertical format.')
    parser.add_argument('--input', required=True,
                    help='input file or directory')
    parser.add_argument('--skip-sentence-splitting', action="store_true",
                    help="Input file contains one sentence per line")


    args = parser.parse_args()
    main(args.input, args.skip_sentence_splitting)
            


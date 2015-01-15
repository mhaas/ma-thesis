#!/usr/bin/python
# -*- coding: utf-8 -*-

# This script downloads movie reviews from <http://www.film-rezensionen.de>.

import leechi
import re
import logging
import sys
import time
import os
import yaml
import StringIO
from bs4 import BeautifulSoup

BASE="http://www.film-rezensionen.de/film-tv/archiv/page/"
MOVIES_PER_PAGE=5

logger = logging.getLogger("film-rezensionen")
logging.basicConfig(filename='film-rezensionen.log',level=logging.DEBUG)

l = leechi.Leechi()

# take care of non-breaking space
# need this to make doc tests work - when loading from file,
# we should have replace the non-breaking space already
# FWIW, BeautifulSoup likely introduces these when it sees
# something like <strong> Hello</strong>
#ratingRE = re.compile(ur"^(\xc2\xa0|\s)?wertung", re.IGNORECASE)
ratingRE = re.compile(ur"^.?wertung", re.IGNORECASE)


def _getWertung(soup):
    """
    # this does not work, so replace \xc2\xa0 on file load
    #>>> soup = BeautifulSoup(u"<em>Wertung:<strong>\xc2\xa02</strong> von 5 </em>")
    #>>> _getWertung(soup)
    #(ur'Wertung: 2\xc2\xa0von 5', 0.4)
    >>> soup = BeautifulSoup(u"<em>Wertung: <strong>2</strong> vom 5 </em>")
    >>> _getWertung(soup)
    (u'Wertung: 2 vom 5', 0.4)
    >>> soup = BeautifulSoup(u"<em>Wertung: <strong>2</strong>von 5 </em>")
    >>> _getWertung(soup)
    (u'Wertung: 2von 5', 0.4)
    >>> soup = BeautifulSoup(u"<em>Wertung: <strong>2</strong> von 5 </em>")
    >>> _getWertung(soup)
    (u'Wertung: 2 von 5', 0.4)
    >>> soup = BeautifulSoup(u"<p><em>Wertung:<strong> 2</strong> von </em>5</p>")
    >>> _getWertung(soup)
    (u'N/A', -1.0)
    # See fr_test.py - the unit tests read from the file and replicate whatever
    # issues we have more faithfully.
    #>>> soup = BeautifulSoup(u'<p style="text-align: justify;"><em> Wertung: <strong>6</strong> von 10</em></p>')
    #>>> _getWertung(soup)
    #(u'Wertung: 6 von 10', 0.6)
    #>>> soup = BeautifulSoup(u'<p style="text-align: justify;"><em> Wertung: <strong>5</strong> von 10</em></p>')
    #>>> _getWertung(soup)
    #(u'Wertung: 5 von 10', 0.5)
    """
    logger.debug(soup)
    ratingNode = soup.find(text=ratingRE)
    if not ratingNode:
        logger.warn("ratingRE did not match anything")
        return (u"N/A", -1.0)
    ratingNode = ratingNode.parent
    # ignore document layout and just work with text
    ratingString = ratingNode.get_text()
    ratingString = ratingString.replace(u"\xc2\xa0", " ")
    logger.debug("ratingString: %s", ratingString)
    # also capture "0,5 von 5"
    # We sometimes get \xc2\xa0, which is a non-breaking space.
    # So we use \s in the regex instead of the good old regular space
    # This still will not remove the \xc2\xa0 in the output, so just replace
    # it when loading..
    valRE = re.compile(ur"(\d,?\d?)\s{0,2}\(?vo(?:n|m)\s{0,2}(\d{1,2})", re.UNICODE)
    valMatch = valRE.search(ratingString)
    
    if not valMatch:
        logger.warn("Could not get rating from: %s", ratingNode)
        #raise Exception("nope.")
        return (u"N/A", -1.0)
    else:
        # fix up float literals
        val = float(valMatch.group(1).replace(",", "."))
        maxVal = float(valMatch.group(2))
    return (ratingString.strip(), val / maxVal)
    

def fetch_as_soup(url, out):
    """Downloads web page and returns as BeautifulSoup object.

    The page is automatically stored to disk. On subsequent calls with the same
    'out' parameter, the page is loaded from disk. This saves a network transfer.
    It is up to you to invalidate, i.e. delete, this cache.
    """
    if os.path.exists(out):
        logger.debug("File %s exists for URL %s, reading from disk", out, url)
        fh = open(out, "r")
        html = fh.read()
        fh.close()
    else:
        html = l.fetchDelayed(url)
        fh = open(out, "w")
        fh.write(html)
        fh.close()
        fh = open(out + ".url", "w")
        fh.write(url)
        fh.write("\n")
        fh.close()
    #soup = BeautifulSoup(html.decode("utf-8"))
    soup = BeautifulSoup(html.decode("utf-8").replace(ur"\xc2\xa0"," "))
    return soup
    


def get_links(index, directory):
    """ Extracts links from archive page.
    
    Given an index for a archive page, the archive page
    is downloaded and all article links are extracted.

    @returns list of URLs
    """
    assert index > 0
    out = os.path.join(directory, "archive-%s.html" % index)
    s = fetch_as_soup(BASE + str(index), out)
    links = s.find_all("a", title=re.compile("Permanent Link") ) 
    links = [a["href"] for a in links]
    return links

def extract(url, directory):
    """Extracts movie review from single article page

    Given an URL pointing to a movie review, this method
    downloads the article and extracts the movie review.
    Some meta information is extracted as well.
    All files are stored to files specified by the 'directory'
    argument.
    """
    logger.info("Extracting information from URL %s", url)
    # extract last part of url, assuming its the title
    assert url[-1] == "/"
    fileName = url.split("/")[-2]
    #out = os.path.join(directory, "%s-%s.html" % (fileName, time.time()) )
    # hope that last part of URL is unique
    out = os.path.join(directory, "%s.html" % (fileName) )
    soup = fetch_as_soup(url, out)
    
    # collect some information
    inner = soup.find("div", {"id" : "inner_content"})
    meta = {}
    meta["title"] = unicode(inner.find("h2").find("a").string)
    meta["author"] = unicode(inner.find("a", {"rel" : "author"}).string)
    meta["authorURL"] = inner.find("a", {"rel" : "author"})["href"]
    meta["URL"] = url
    categoriesNode = soup.find("span", {"class" : "categories"})
    categories = categoriesNode.find_all("a", {"rel" : re.compile("category")})
    meta["categories"] = [a["href"] for a in categories]

    textNode = soup.find("div", {"class" : "entry-content"})
    (ratingText, rating) = _getWertung(textNode)
    meta["rating"] = rating
    meta["ratingText"] = ratingText
    meta["dateText"] = inner.find("div", {"class" : "date"})

    fh = open(out + ".meta", "w")
    yaml.dump(meta, fh)
    fh.close()

    # clean up
    # filter "related articles"
    soup.find("div", {"class" : "yarpp-related" }).clear()
    # filter image caption and other noise
    noiseNodes = soup.find_all("span", {"style" : re.compile(ur"font-size: x-small;?")})
    noiseNodes.extend(soup.find_all("span", {"style" : re.compile(ur"font-size: 85%;?")}))
    noiseNodes.extend(soup.find_all("p", {"style" : re.compile(ur"font-size: 10px; text-align: justify;?")}))
    for noise in noiseNodes:
        noise.clear()

    # Wrap movie names in quotes
    # TODO: does this work for linked movies all the time?
    # TODO: verify this works on embedded a 
    for em in textNode.find_all("em"):
        if not "wertung" in em.get_text().lower():
            em.insert(0, "--EM-REPLACEMENT--")
            em.append("--EM-REPLACEMENT-END--")
    for strong in textNode.find_all("strong"):
        strong.insert(0, "--STRONG-REPLACEMENT--")
        strong.append("--STRONG-REPLACEMENT-END--")
    
    reviewBuf = StringIO.StringIO();
    # TODO: this ignores top-level span elements
    # older articles use div
    for node in textNode.find_all(re.compile(ur"(p|div)"), {"style" : re.compile(ur"text-align: justify;?")}):
        text = node.get_text()
        if ratingRE.search(text):
            continue
        reviewBuf.write(text)
        reviewBuf.write(" ")
    fh = open(out + ".txt", "w")
    fh.write(reviewBuf.getvalue().encode("utf-8"))
    fh.close()
    reviewBuf.close()

def main(directory):
    """Main method. Downloads all reviews to 'directory'.
    """
    index = 1
    while True:
        logger.info("Working on index page %s", index)
        links = get_links(index, directory)
        for link in links:
            r = extract(link, directory)
        if len(links) < MOVIES_PER_PAGE:
            break
        index += 1

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Provide output directory!"
        sys.exit(-1)
    main(sys.argv[1])
    


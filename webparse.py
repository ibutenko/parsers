from html.parser import HTMLParser
import urllib.request
from urllib.parse import urljoin
import logging

# Program to parse a Web page
rooturl = ''

# Is this a valid tag?
validtag = False

# Link URL
linkurl = ''

# List of valid tags
validtags = ['a', 'title']
### 'p', 'h3', 'h2', 'h1', 'li', 'div']
# 'span', 

# Ignore before string
ignorebefore = ''
ignoredstringfound = False

# dictionary to store articles and URLs
pagedictionary={}
linkdictionary={}

# Add a link to linkdictionary, verify it is unique etc.
# Duplicate items pointing to the same page will be merged.
def addToLinkDictionary(link, text):
    if link in linkdictionary.keys():
        if not text in linkdictionary[link]:
            linkdictionary[link] = linkdictionary[link] + ' | ' + text
    else:
        linkdictionary[link] = text.strip()

# Generate page dictionary from linkdictionary.
def generatePageDictionary():
    global pagedictionary
    for key in linkdictionary.keys():
        pagedictionary[linkdictionary[key]] = key

# Process parsed output tags and strings and display text and URLs
def ProcessParsedOutput(inputdata, inputtype):
    global validtag
    global linkurl
    global ignoredstringfound

    if inputtype == 'starttag':
        if inputdata in validtags:
            validtag = True
        else:
            logging.info('Ignored tag: %s', inputdata)

    if inputtype == 'endtag':
        if inputdata in validtags:
            validtag = False;
        
    if inputtype == 'parsedtext':
        if not ignoredstringfound:
            if ignorebefore == '':
                ignoredstringfound = True
            else:
                if inputdata.strip() == ignorebefore:
                    ignoredstringfound = True

        if not ignoredstringfound:
            return
        
        if validtag:
            if inputdata.strip() != '':
                logging.info('Valid string found: %s', inputdata.strip())
                if linkurl != '':
                    if not linkurl.startswith('http://'):
                        linkurl = urljoin(rooturl, linkurl)
                    logging.info('URL: %s \n', linkurl)
                    addToLinkDictionary(linkurl, inputdata.strip())
        else:
            logging.info('String with no valid tag: %s', inputdata)
    

# HTML parser
class MyHTMLParser(HTMLParser):
    starttag  = '';
    endtag  = '';
    parsedtext  = '';

    def handle_starttag(self, tag, attrs):
        global linkurl
        starttag = tag
        ProcessParsedOutput(starttag, 'starttag')
        if tag == 'a':
           # Check the list of defined attributes.
           for name, value in attrs:
               # If href is defined, this is the URL we need.
               if name == "href":
                   linkurl = value

    def handle_endtag(self, tag):
        endtag = tag
        ProcessParsedOutput(endtag, 'endtag')
        if tag == 'a':
            linkurl = ''

    def handle_data(self, data):
        global linkurl
        parsedtext = data
        ProcessParsedOutput(parsedtext, 'parsedtext')


def parseWebPage(url):
    # Open a site
    # Simulate Chrome to avoid "403/Forbidden" situation
    global rooturl

    rooturl = url
    req = urllib.request.Request(rooturl, data=None, 
        headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
                }
        )

    logging.info('Page URL to parse: %s', rooturl)

    ignoredstringfound = False

    with urllib.request.urlopen(req) as response:
       the_page = response.read().decode("utf-8") 

    # Parsing method #1: HTMLParser
    parser = MyHTMLParser()
    parser.feed(the_page)

    generatePageDictionary()
    return pagedictionary

def init():
    pagedictionary.clear()
    linkdictionary.clear()

###! /usr/bin/python

__author__="Krutika Shetty <kjs2154@columbia.edu>"
__date__ ="$Nov 26, 2012"

import sys
import math
import re
from collections import OrderedDict, defaultdict
import os
import nltk
import pickle
from xml.dom import minidom
from xml.dom import EMPTY_NAMESPACE
import nltk
from nltk.stem.porter import PorterStemmer
import time

title_dict = {}     ## dictionaries storing the extracted and parsed search results
desc_dict = {}
url_dict = {}
ser_cnt = 0         ## search counte - will act as document ids



def get_text_from_construct(element):
    '''
    Return the content of an Atom element declared with the
    atomTextConstruct pattern.  Handle both plain text and XHTML
    forms.  Return a UTF-8 encoded string.
    '''
    
    if element.getAttributeNS(EMPTY_NAMESPACE, u'type') == u'xhtml':
        #Grab the XML serialization of each child
        childtext = [ c.toxml('utf-8') for c in element.childNodes ]
        #And stitch it together
        content = ''.join(childtext).strip()
        return content
    elif element.firstChild == None:
        return ""
    else:        
        return element.firstChild.data.encode('utf-8')



def parse_atom():
    '''
    This function will take the modified xml file and populate the search result dictionaries with the parsed snippets, title and url.
    This parser is specifically used for 'atom' formatted xml files.
    ''' 
    global ser_cnt
    
    ATOM_NS = 'http://www.w3.org/2005/Atom'

    doc = minidom.parse('modified.xml')
    #Ensure that all text nodes can be simply retrieved
    doc.normalize()

    for entry in doc.getElementsByTagNameNS(ATOM_NS, u'entry'):                     ## each search result is marked by an <entry> tag
        ser_cnt += 1
        title_dict[ser_cnt] = {}
        desc_dict[ser_cnt] = {}
        url_dict[ser_cnt] = {}
        
        #First title element in doc order within the entry is the title
        title = entry.getElementsByTagNameNS(ATOM_NS, u'Title')[0]                  ## title marked by <Title> tag
        title_dict[ser_cnt] = get_text_from_construct(title)                        ## call the get text function to get the unicode text from the title element

        desc = entry.getElementsByTagNameNS(ATOM_NS, u'Description')[0]             ## snippets marked by <Description> tag
        desc_dict[ser_cnt] = get_text_from_construct(desc)                          ## call the get text function to get the unicode text from the description element

        url = entry.getElementsByTagNameNS(ATOM_NS, u'Url')[0]                      ## url marked by <Url> tag
        url_dict[ser_cnt] = get_text_from_construct(url)                            ## call the get text function to get the unicode text from the url element 

    return



def parse_file(interim_path):
    '''
    This function will take the path where the search results are stored as input,
    and call the 'atom' parser function for parsing
    '''

    dirlist = os.listdir(interim_path)                          ## list all the search result files

    for search_file in dirlist:                                 ## for each of the search result xml files
        
        fi = open(interim_path + "//" + search_file,"r")
        fo = open("modified.xml","w")                           ## modify the xml file slightly to extract the snippets, title and description easily
        lines = fi.read()
        lines = lines.replace("m:properties","properties")
        lines = lines.replace("d:Title","Title")
        lines = lines.replace("d:Description","Description")
        lines = lines.replace("d:Url","Url")
        fo.write(lines)
        fo.close()
        fi.close()

        parse_atom()                                            ## call the function to parse the 'atom' format xml file

    pickle.dump(title_dict,open("title_dict","wb"))
    pickle.dump(desc_dict,open("desc_dict","wb"))
    pickle.dump(url_dict,open("url_dict","wb"))







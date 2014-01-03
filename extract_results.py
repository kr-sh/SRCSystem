#!/usr/bin/python

__author__="Krutika Shetty <kjs2154@columbia.edu>"
__date__ ="$Nov 26, 2012"


import urllib2
import base64
import pprint
import json
import os

def get_search_results(q):
    '''
        This function takes the query as input and extracts the search results for that query
        using the BING API.
        It stores the extracted search results in a new interim directory 
    '''

    interim_path = ".//interm_dir"                                              ## creating a temporary directory in the current path to store search result files
    if not os.path.exists(interim_path):                                        ## if intermediate folder does not exist, create it
        os.makedirs(interim_path)

    ''' get the top 100 results (BING API extracts only 50 as of now)
        hence call search twice to extract a total of 100 results
    '''

    n = str(100)                                            
    bingUrl = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Web?Query=%27'+q+'%27&Market=%27en-US%27&$top='+n+'&$format=Atom'
                                                                                ## Provide your account key here
    accountKey = '9htjdq6bRqnIrH5QrBh9LLyC9qVzZBLC+sflPBDjbMU='

    accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
    headers = {'Authorization': 'Basic ' + accountKeyEnc}
    req = urllib2.Request(bingUrl, headers = headers)
    response = urllib2.urlopen(req)
    content = response.read()
                                                                                ## content contains the xml/json response from Bing.
    results_file_name = 'search_results_1.xml'                                  ## stores the 1st batch of results in search_results_1 file 
    fo = open(interim_path + "//" + results_file_name,'w')
    fo.write(content)
    fo.close()
                                                                                ## extract 50 more results
    bingUrl = 'https://api.datamarket.azure.com/Data.ashx/Bing/SearchWeb/v1/Web?Query=%27'+q+'%27&Market=%27en-US%27&$skip=51&$top='+n+'&$format=Atom'
    accountKey = '9htjdq6bRqnIrH5QrBh9LLyC9qVzZBLC+sflPBDjbMU='
    accountKeyEnc = base64.b64encode(accountKey + ':' + accountKey)
    headers = {'Authorization': 'Basic ' + accountKeyEnc}
    req = urllib2.Request(bingUrl, headers = headers)
    response = urllib2.urlopen(req)
    content = response.read()
    results_file_name = 'search_results_2.xml'                                  ## stores the 2nd batch of results in search_results_2 file      
    fo = open(interim_path + "//" + results_file_name,'w')
    fo.write(content)
    fo.close()   
    

    return interim_path                                                         ## return the interim path to the parser





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

title_dict = {}                         ## initializing variables
desc_dict = {}
url_dict = {}

index =  {}
np_ind = {}
doc_word_dict = {}
doc_np_dict = {}

norm_doc_word_dict = {}
dij = {}
cluster = {}

label_dict = {}

import extract_results                  ## importing all user defined modules
import parsing_search_results
import indexing
import clustering
import labeling

##interim_path = ".//interm_dir"          ## initializing variables


if __name__ == "__main__":

        if len(sys.argv)!=1: 
                sys.exit(2)
        query = raw_input("Please enter the search string: ")             ## Expect exactly 2 arguments: the search query and number of clusters
        k = raw_input("Please enter the number of clusters: ")
        k=int(k)
##        query = "jaguar"
        start = time.clock()
##        k=7
        interim_path = extract_results.get_search_results(query)        ## extract search results
               
        parsing_search_results.parse_file(interim_path)                 ## parse the serach results
        title_dict = pickle.load(open("title_dict","rb"))               ## unpickle the document dictionaries
        desc_dict = pickle.load(open("desc_dict","rb"))
        url_dict = pickle.load(open("url_dict","rb"))

        
        indexing.create_index(title_dict,desc_dict,url_dict)            ## create an index
        index = pickle.load(open("index","rb"))                         ## unpickle the index dictionaries
        np_ind = pickle.load(open("np_ind","rb"))
        stem_dict = pickle.load(open("stem_dict","rb"))
        
        indexing.calc_tf_idf(title_dict,index,np_ind)                   ## calculate the tf-idf values for the document vector
        doc_word_dict = pickle.load(open("doc_word_dict","rb"))         ## unpickle the tf-idf dictionaries representing document vectors
        doc_np_dict = pickle.load(open("doc_np_dict","rb"))

        norm_doc_word_dict = clustering.normalize_doc_dict(doc_word_dict)               ## normalize the document vector
        dij = clustering.calc_eucl_dist(norm_doc_word_dict)                             ## calculate the eucledian distance
        clustering.get_mediods(k,dij)                                                   ## use k-mediods to get the clusters
        cluster = pickle.load(open("cluster","rb"))                                     ## unpickle the clusters

        
        label_dict = labeling.label(cluster,doc_np_dict, stem_dict,np_ind,query)                        ## label the clusters
        labeling.display_clustered_snippets(label_dict, cluster, title_dict, desc_dict, url_dict, k)    ## display the clustered search results

        elapsed = (time.clock() - start)
        print "time elapsed:", elapsed



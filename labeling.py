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


label_dict = {}

def label(cluster, doc_np_dict, stem_dict,np_ind,query):
    ''' This function creates labels for the clusters using the NP dictionaries
        and frequency of NPs among the documents in the cluster.
        It chooses the 6 highest frequency NPs as cluster labels for each cluster.
    '''

    
    for med in cluster:                                                                         ## for each cluster
        temp = {}

        for docid in cluster[med]:                                                              ## calculate the NP frequencies of the documents in the cluster
            for word in np_ind:
                if docid in np_ind[word]:
                    if word in temp and word != query:
                        temp[word] = [temp[word][0] + np_ind[word][docid],stem_dict[word][docid]]
                    elif word != query:
                        temp[word] = [np_ind[word][docid],stem_dict[word][docid]]        

                            
        label_dict[med] = set()


        for word,val in sorted(temp.iteritems(), key=lambda x:x[1][0], reverse=True)[:6]:       ## extract the top 6 NPs as labels for the cluster
            label_dict[med].add(val[1])

    return label_dict

            

def display_clustered_snippets(label_dict, cluster, title_dict, desc_dict, url_dict,k):
    ''' This function takes the labels from the labeling functiona and displays the cluster labels with
        the search results under that cluster
    '''
    cluster_no = 0
    clus_res = {}

    for med,i in zip(cluster, range(1,len(cluster)+1)):
        clus_res[i] = med
        
    while (cluster_no != 'Q'):

        print "\nClusters:"
        for med,i in zip(cluster, range(1,len(cluster)+1)):
            label = '; '.join(label_dict[med])
            print ("%i: %s\n" % (i, label))

        cluster_no = raw_input("Select option:  [cluster number] for individual clusters\n\t\t['A'] for all results\n\t\t['Q'] to quit\nOption? - ")

        if cluster_no in str(range(1,k+1)):
            med = clus_res[int(cluster_no)]
            label = '; '.join(label_dict[med])
            print "Labels: ", label, "\n" 
            for docid in cluster[med]:
                print "Title:"
                print title_dict[docid]
                print "Description:"
                print desc_dict[docid]
                print "URL:"
                print url_dict[docid]
                print "\n"

        elif cluster_no == 'A':
            for med,i in zip(cluster, range(1,len(cluster)+1)):
                label = '; '.join(label_dict[med])
                print ("---------------------------Cluster %i:------------------------" %i)
                print "Labels: ", label, "\n" 
                for docid in cluster[med]:
                    print "Title:"
                    print title_dict[docid]
                    print "Description:"
                    print desc_dict[docid]
                    print "URL:"
                    print url_dict[docid]
                    print "\n"
        elif cluster_no != 'Q':
            print "Please select one of the given options:"
            continue
    



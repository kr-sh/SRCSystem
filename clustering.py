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


norm_doc_word_dict = {}
dij = {}
pij = {}
cluster = {}                    ## cluster dictionary stores the mediods and their corresponding document clusters as cluster[mediod] = [document in the cluster]


def find_seeds(k):
    ''' This function takes the number of clusters as input, and using the MAX-MIN algorithm
        calculates the intial k seeds to paas to the k-mediods algorithm.
    '''

    max_dist = float("-inf")
    seeds = set()
    
    for doc_i in dij:                               ## calculation for initializing the mediods
        for doc_j in dij:                           ## the first 2 seeds are the documents with the maximum eucledian distance
            if dij[doc_i][doc_j] > max_dist:
                max_dist = dij[doc_i][doc_j]
                s1 = doc_i
                s2 = doc_j
    seeds.add(s1)
    seeds.add(s2)

    while (len(seeds) < k):                         ## until number of seeds =k, get the document with the maximum minimum eucledian distance from the other seeds
        max_min_dist = float("-inf")
        for doc_i in dij:
            if doc_i not in seeds:
                min_dist = float("inf")
                for seed in seeds:
                    if dij[doc_i][seed] < min_dist:
                        min_dist = dij[doc_i][seed]
                if min_dist > max_min_dist:
                    max_min_dist = min_dist
                    new_seed = doc_i
            else:
                continue
        seeds.add(new_seed)
        
    return seeds
            

def normalize_doc_dict(doc_word_dict):
    ''' This funtion takes the document vector with tf-idf values
        and creates a new normalized document vector.
    '''
    norm_sum = {}
   
    for docid in doc_word_dict:
        nsum = 0
        for word in doc_word_dict[docid]:
            nsum = nsum + math.pow(doc_word_dict[docid][word],2)
        norm_sum[docid] = math.sqrt(nsum)
        
    for docid in doc_word_dict:
        norm_doc_word_dict[docid] = {}
        for word in doc_word_dict[docid]:   
            norm_doc_word_dict[docid][word] = float(doc_word_dict[docid][word]/norm_sum[docid])


    return norm_doc_word_dict

def calc_eucl_dist(norm_doc_word_dict):
    ''' This funtion takes the normalized document vector
        and creates a dictionary storing eucledian distance values for each document pair.
        eucl-dist(i,j) = sqrt( sum( squares (i[tf-idf] - j[tf-idf]) ) )
    '''
    
    for doc_i in norm_doc_word_dict:
        dij[doc_i] = {}
        for doc_j in norm_doc_word_dict:
            summ = 0
            for word in norm_doc_word_dict[doc_j]:
                summ = summ + math.pow(norm_doc_word_dict[doc_j][word] - norm_doc_word_dict[doc_i][word],2)
            dij[doc_i][doc_j] = math.sqrt(summ)

    return dij
            
def get_mediods(k,dij):
    ''' This function takes the input as number of clusters and the normalized document vectors
        and using the k-mediods algorithm calculates the k clusters.
    '''

    for doc_i in dij:                               ## calculation for initializing the mediods
        sumi = 0
        pij[doc_i] = {}
        for doc_j in dij:
            sumi = sumi + dij[doc_i][doc_j]
        pij[doc_i] = sumi

    seeds = find_seeds(k)                           ## call the get seeds function for seed initialization
    for seed in seeds:
        cluster[seed] = set()                       ## initialze the seeds as cluster mediods


    optimal = {}
    optimal[0] = 0.0
    cluster_d = {}                                  ## this dictionary maps a document to its mediod
    
    for itr in range(1,16):                         ## number of iteration is give as 15 but termination is decided by optimal val of the clusters
        
        for docid in dij:                           ## assigning the documents to clusters
            min_d = float("inf")
            for med in cluster:
                if dij[docid][med] < min_d:
                    cl_i = med
                    min_d = dij[docid][med]
            cluster_d[docid] = cl_i
            cluster[cl_i].add(docid)                ## adding the document to its cluster
                
        optimal[itr] = 0
        for docid in dij:                           ## calculate the optimal value of the clusters 
            optimal[itr] = optimal[itr] + dij[docid][cluster_d[docid]]
        
        if optimal[itr] == optimal[itr-1]:          ## if the optimal value in this iteration is equal to that of the previous iteration, stop the algorithm]
            break
                                                    ## else
        new_mediods = set()
        old_mediods = set()
        for med in cluster:                         ## re-calculate the mediods
            min_m = float("inf")
            for doc_i in cluster[med]:
                sumi = 0
                for doc_j in cluster[med]:
                    sumi = sumi + dij[doc_i][doc_j]
                if  sumi < min_m:
                    new_med = doc_i
                    min_m = sumi
            old_mediods.add(med)
            new_mediods.add(new_med)
            
        for med in old_mediods:
            del cluster[med]
        
        for med in new_mediods:                     ## create new cluster mediods and continue to next iteration
            cluster[med] = set()
        

    pickle.dump(cluster,open("cluster","wb"))
        







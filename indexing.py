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


index =  {}
np_ind = {}
porter = nltk.PorterStemmer()
doc_word_dict = {}
doc_np_dict = {}
stem_dict = {}


def get_chunks(sent):
    ''' This function takes the entire search result and finds all the noun phrases (NP)
        in it and returns them to the indexing function 
    '''
    noun_phrases = list()
 
    words = nltk.word_tokenize(sent)                                    ## first tokenize the search result- treated as a sentence here
    tagged_sent = nltk.pos_tag(words)                                   ## perform part-of-speech tagging
                                                                        ## define patterns to extract NPs
    pattern = """                                                       

    NP: {<NNP>+<NN>}
        |{<NN>+<NNP>}
        |{<JJ>*<NN>}
        |{<NNP>+<NNS>}
        |{<NNP>+}
        |{<NN>+} 
    """

    NPChunker = nltk.RegexpParser(pattern)                              ## define NLTK chunker to extract the defined NPs 
    result = NPChunker . parse(tagged_sent)
    
    for subtree in result.subtrees(filter=lambda t: t.node == 'NP'):
        np = ""
        for nodes in subtree.leaves():                                  ## get the noun phrase as a list of words
            np = np + ' ' + nodes[0]
        noun_phrases.append(np.strip())                                 ## return the list of NPs

    return noun_phrases



def calc_tf_idf(title_dict,index,np_ind):
    ''' This function takes the indexes and calculates the tf-idf values
        which are stored in new doc-word and doc-NP dictionaries. These now
        act as document vectors in the VSM.
    '''
    
    N = len(title_dict)             ## N = number of documents i.e. search results

    ## calculating tf-idf for words
    
    for docid in title_dict:
        for word in index:
            try:
                tf = index[word][docid]                             ## get tf
                idf = math.log(N/len(index[word]),2)                ## get idf
                tf_idf = tf * idf                                   ## calculate tf-idf = tf * idf
            except:
                tf_idf = 0
            if doc_word_dict.__contains__(docid):                   ## check if index contains the doc
                doc_word_dict[docid][word] = tf_idf                 ## if yes, create a tf-idf entry for the word
            else:                                                   ## if doc not in index, create an index entry for this doc and word
                 doc_word_dict[docid]= {}
                 doc_word_dict[docid][word] = tf_idf

            
    pickle.dump(doc_word_dict,open("doc_word_dict","wb"))

    ## calculating tf-idf for noun phrases np_ind[s_phrase][docid]
    
    for docid in title_dict:
        for s_phrase in np_ind:
            try:
                tf = np_ind[s_phrase][docid]
                idf = math.log(N/len(np_ind[s_phrase]),2)
                tf_idf = tf * idf
            except:
                tf_idf = 0
            if doc_np_dict.__contains__(docid):                     ## check if index contains the doc
                doc_np_dict[docid][s_phrase] = tf_idf               ## if yes, create a tf-idf entry for the NP
            else:                                                   ## if doc not in index, create an index entry for this doc and word
                 doc_np_dict[docid]= {}
                 doc_np_dict[docid][s_phrase] = tf_idf

    pickle.dump(doc_np_dict,open("doc_np_dict","wb"))
    


def create_index(title_dict,desc_dict,url_dict):
    ''' This function takes the search result dictionaries and creates an inverted index - word-document index
        and a phrase index for Noun Phrases extracted using chunking.
        It also does pre-processing such as lower-casing, stemming, stop-word removal
        and removing <3 letter words from the index.    
    '''

    ## creating inverted index storing word-document frequency i.e term frequecy in the doc

    for docid in title_dict:                                        
        doc = title_dict[docid] + ' ' + desc_dict[docid] + ' ' + url_dict[docid]        ## concatenate all parts of the search result
        words = (re.findall(r'\w+', doc,flags = re.UNICODE | re.LOCALE))                ## extract words from the text

        for word in words:                                      ## for each word
            word = word.lower().strip()                         ## lower-case the word
            word = porter.stem(word)                            ## stemming the words before inserting into the index
            if index.__contains__(word):                        ## check if index contains the word
                if index[word].__contains__(docid):             ## check if there is a doc containing this word
                    index[word][docid] += 1                     ## if yes, increment the word-doc count
                else:                                           ## else create an entry for this new doc containing this word with frequency = 1
                    index[word][docid] = 1
            else:                                               ## if word not in index, create an index entry for this word
                 index[word]= {}
                 index[word][docid] = 1                 

    ## creating noun-phrase index

    for docid in title_dict:                                        
        doc = title_dict[docid] + ';' + desc_dict[docid] + ';' + url_dict[docid]
        sent = doc.replace('.',';')                             ## modifying the search result to make NP extraction easy
        sent = sent.replace('/',';')
        sent = sent.replace('|',';')
        sent = sent.replace('(',' ')
        sent = sent.replace(')',' ')
        sent = sent.replace('_',' ')
        np = get_chunks(sent)                                   ## call chunking function on the search result
        
        for phrase in np:                                       ## for each NP
            phrase = phrase.lower().strip()                     ## lower-case the NP
            s_phrase = porter.stem(phrase)                      ## stemming the NP before inserting into the index
            if np_ind.__contains__(s_phrase):                   ## check if index contains the NP
                if np_ind[s_phrase].__contains__(docid):        ## check if there is a doc containing this NP
                    np_ind[s_phrase][docid] += 1                ## if yes, increment the NP-doc frequency
                else:                                           ## else create an entry for this new doc containing this NP
                    np_ind[s_phrase][docid] = 1
                stem_dict[s_phrase][docid] = phrase             ## store the orignal words mapped with the stemmed words
            else:                                               ## if NP not in index, create an index entry for this NP
                 np_ind[s_phrase]= {}
                 np_ind[s_phrase][docid] = 1
                 stem_dict[s_phrase] = {}
                 stem_dict[s_phrase][docid] = phrase
        
    ## stopwords from nltk.corpus
    stopwords = ['org','html','www','http','com','i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now']

    for word in stopwords:                                      ## removing stop-words from the indexes
        word = word.lower().strip()
        word = porter.stem(word)
        if word in index.keys():
            del index[word]
        if word in np_ind.keys():
            del np_ind[word]

    ## removing words of length smaller than 3 letters from index
    small_words = set()
    for word in index:
        if len(word) < 3:
            small_words.add(word)
    for word in small_words:
        del index[word]

    ## removing words of length smaller than 4 letters from NP index
    small_words = set()
    for np in np_ind:
        if len(np) < 4:
            small_words.add(np)
    for np in small_words:
        del np_ind[np]
        
    ## pickle the index dictionaries
    pickle.dump(index,open("index","wb"))
    pickle.dump(np_ind,open("np_ind","wb"))
    pickle.dump(stem_dict,open("stem_dict","wb"))







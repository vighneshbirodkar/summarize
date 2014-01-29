import re
import os
import math
import itertools
import random

from .. import __DEBUG__

__DFACTOR__ = .85

import sys
sys.path.append('..')
sys.path.append('/usr/lib/graphviz/python/')
sys.path.append('/usr/lib64/graphviz/python/')
#import gv


from pygraph.classes.graph import graph
#from pygraph.classes.digraph import digraph
#from pygraph.algorithms.searching import breadth_first_search
#from pygraph.readwrite.dot import write




class Sentence(object):
    """
    
    A sentence , basically a wrapper around a list of words
    
    """
    
    def __init__(self,string):
        self.string = string
        self.words_ = []
        matchIter = re.finditer('[\w]+',string)
        self.len_ = 0
        self.score = random.random()/2 # random number between 0 and 3
        self.influenceScore = 0.0
        for match in matchIter:
            self.len_ += 1
            term = match.group().lower()
            self.words_.append(term)
        if self.len_ <= 1 :
            #A sentence with one word is highly unlikely
            #Also causes problem with log
            raise ValueError

    
    def __str__(self):
        return self.string
    
    def __len__(self):
        return self.len_
    
    def words(self):
        return self.words_

    def similarity(self,other):
        count = 0
        for w1 in self.words() :
            for w2 in other.words() :
                if w1 == w2 :
                    count += 1

        return count/(math.log(len(self)) + math.log(len(other)))

    def getScore(self):
        return self.score

    def setScore(self,score):
        self.score = score

    def getInfluencedScore(self):
        return self.score - self.influenceScore

class Document(object):
    """
    
    A class represnting a text document and all the relevant information
    
    """
    regex = re.compile(r'([A-Z][^\.!?]*[\.!?])')
    def __init__(self,fileName,_set = None):
        """
        Creates a Document object
        
        Args:
            fileName : Name of the file to use.
        
        """
        
        self.sentences_ = []
        self.graph = None
        self.coGraph = None
        self.fn = fileName
        self.textRank = False
        with open(fileName, 'r') as f:
            for line in f:
                list_ = Document.regex.split(line.strip())
                for s in list_ :
                    s = s.strip()
                    if len(s) > 0 :
                        #print 'string = ' , '" ',s,' "'
                        try :
                            self.sentences_.append(Sentence(s))
                        except ValueError:
                            #No Valid word was found
                            pass


    def sentences(self):
        return self.sentences_
    
    def genSummary(self,compression = 0.10):
        
        self.doTextRank()
        self.sentences_ = sorted(self.sentences_,key = Sentence.getInfluencedScore)
        retVal = []
        count = compression * len(self.sentences())
        for i in range(1,int(count+1)):
            retVal.append( str(self.sentences_[-i]) )
    
        return retVal
        

    def doTextRank(self,error = 0.001):
        if(self.textRank):
            return
        if (__DEBUG__):
            print 'Starting to Create Graph for',self.fn

        self.textRank = True
        self.graph = graph()
        self.graph.add_nodes(self.sentences())
        
        for pair in itertools.combinations(self.sentences(), 2):
            #print pair[0].similarity(pair[1])
            self.graph.add_edge(pair,wt = pair[0].similarity(pair[1]))

        # Remove sentences that are to dissimilar with any other sentence
        # Makes denominator in PR formula 0
        # I dont really know what is supposed to be done here

        for s in self.sentences() :
            total = sum([self.graph.edge_weight((s,n)) for n in self.graph.node_neighbors[s]])
            if total < 0.001 :
                self.graph.del_node(s)
                self.sentences_.remove(s)

        #print len(self.sentences())
        totalUpdate = 100.0
        while  totalUpdate > error:
            totalUpdate = 0
            i = 0
            for s in self.sentences() :

                oldValue = s.getScore()
                total = 0
                for n in self.graph.node_neighbors[s] :
                    wt = self.graph.edge_weight((s,n))
                    score = n.getScore()   
                    
                    num = score*wt
                    # sum of edge wieghts of all neighbours of n
                    # Magnificent !!
                    den = sum([self.graph.edge_weight((n,m)) for m in self.graph.node_neighbors[n] ] )

                    total += num/den
                    
                s.setScore( (1 - __DFACTOR__) + __DFACTOR__*total)
                update = abs(s.getScore() - oldValue)
                totalUpdate += update
            if __DEBUG__ : 
                print 'Text Rank Iteration, Error = ',totalUpdate
        



class DocumentSet(object):
    """
    
    A class represnting a collection of documents.
    
    """
    def __init__(self,directory,_set = None):
        """
        Creates a Document Set, a collection of documents
        
        Args:
            dirName : The directory to look for files
        
        """
        
        self.documents = []
        self._terms = set([])
        self.idf = {}
        self.tfidf = None
        for name in os.listdir(directory):
            fileName = directory + os.sep + name
            doc = Document(fileName)
            doc._set = self
            self.documents.append(doc)
            #self._terms = self._terms.union(doc.terms())
        

            
    def docs(self):
        """
        Get the list of documents in the Set
        
        Returns:
            A List of Document Objects.
        
        """
        
        return self.documents
        




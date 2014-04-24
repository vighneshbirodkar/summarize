import re
import os
import math
import itertools
import random
import logging
from sklearn.svm import SVR

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
    
    A sentence , basically a wrapper around a list of words, with some others
    functions defined
    
    """
    
    def __init__(self,string,idx):
    
        self.index = idx
        self.string = string
        self.words_ = []
        #prob that sentence exists
        self.probability = None 

        #probablity that this sentence contributed to a given summary
        self.contribProbability = None

        #probablity that this sentence is in a summary given a basedoc
        self.summaryProbablity = None

        #the gaussian overlap
        self.go = None
        
        #the importance given a summary
        self.importance = None
        

        #the fso overlap
        self.fso = None
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

    def __repr__(self):
        return self.string
    
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

    def getInfluence(self):
        return self.influenceScore

    def addInfluenceFrom(self,baseDoc,influence):
        w = 0
        for pair in itertools.combinations(self.words(), 2):
            #print pair[0],pair[1]
            w += baseDoc.getCoGraphWeight(pair[0],pair[1])/len(self)
        self.influenceScore = influence * w
        #print "w = ",w,"len = ",len(self)

    def addCooccurProbability(self,baseDoc):
        w = 0
        baseDoc.doCoGraph()
        for pair in itertools.combinations(self.words(), 2):
            #print pair[0],pair[1]
            w += baseDoc.getCoGraphWeight(pair[0],pair[1])/len(self)
        self.summaryProbability = w
        
        

class Document(object):
    """
    
    A class represnting a text document and all the relevant information
    
    """
    regex = re.compile(r'[\.!?]')
    #print '\n\n\n'
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
        self.coOccurDone = False
        self.featuresGenerated = False
        self.wordCount = {}
        count = 0
        with open(fileName, 'r') as f:
            line = f.read()
            list_ = Document.regex.split(line.strip())
            for s in list_ :
                s = s.strip()
                s = s.split('\n')
                s = ' '.join(s)
                if len(s) > 0 :
                    #print 'string = ' , '" ',s,' "'
                    try :
                        count += 1
                        self.sentences_.append(Sentence(s,count))
                    except ValueError:
                        #No Valid word was found
                        pass
        #print '\n\n\n' + str(self.sentences_) + '\n\n\n'
        
        for sentence in self.sentences_:
            for word in sentence.words_:
                try:
                    self.wordCount[word] += 1
                except KeyError:
                    self.wordCount[word] = 1
        
        self.totalWords = len([self.wordCount[x] for x in self.wordCount.keys()])
        
    def sentences(self):
        return self.sentences_
    
    def genSummary(self,compression = 0.10,base = None,influence = 0.01):
        
        self.doTextRank()
        if base == None :
            self.sentences_ = sorted(self.sentences_,key = Sentence.getScore)
            retVal = []
            count = compression * len(self.sentences())
            for i in range(1,int(count+1)):
                retVal.append( str(self.sentences_[-i]) )
                #print self.sentences_[-i].getScore()
                
        
            return retVal
        else :
            base.doCoGraph()
            self.addInfluenceFrom(base,influence)
            self.sentences_ = sorted(self.sentences_,key = Sentence.getInfluencedScore)
            retVal = []
            count = compression * len(self.sentences())
            for i in range(1,int(count+1)):
                retVal.append( str(self.sentences_[-i]) )
                print self.sentences_[-i].getScore(),self.sentences_[-i].getInfluence()
        
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
        # I dont really know what is supposed to be done here, Vig

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

            logging.info('Text Rank Iteration, Error = %f' % totalUpdate)
    
    def doCoGraph(self):
        if self.coOccurDone :
            return
        
        logging.info('Computing Co Graph')
        self.coOccurDone = True
        self.coGraph = graph()
        for s in self.sentences():
            for pair in itertools.combinations(s.words(), 2):
                if self.coGraph.has_edge(pair):
                    w = self.coGraph.edge_weight(pair)
                    self.coGraph.set_edge_weight(pair,wt = w + 1)
                else :
                    if not self.coGraph.has_node(pair[0]):
                        self.coGraph.add_node(pair[0])
                    if not self.coGraph.has_node(pair[1]):
                        self.coGraph.add_node(pair[1])
                    self.coGraph.add_edge(pair,wt = 1)


    def getCoGraphWeight(self,word1,word2):
        
        self.doCoGraph()
        if self.coGraph.has_edge((word1,word2)):
            return self.coGraph.edge_weight((word1,word2))/math.log(len(self.sentences()))
        else:
            return 0

    def addInfluenceFrom(self,base,influence):
        for s in self.sentences():
            s.addInfluenceFrom(base,influence)
    
    def getFSOverlap(self, sentence):
        """
        Gets the First Sentence Overlap of a given sentence.
        
        Args:
            sentence : The sentence for which to compute FSO
        
        """
        return sentence.similarity(self.sentences_[0])
    
    def getLocalOverlap(self, idx_s, weights):
        """
        Gets the Local Overlap of a given sentence.
        
        Args:
            idx_s   : The position of sentence in the document.
            weights : Weight vector for local similarity, ordered by level
        
        """
        score = 0
        level = 1
        for weight in weights:
            if (idx_s - level) >= 0:
                score = score + weight * (self.sentences_[idx_s].similarity(self.sentences_[idx_s-level]))
            if (idx_s + level) < len(self.sentences_):
                score = score + weight * (self.sentences_[idx_s].similarity(self.sentences_[idx_s+level]))
            level = level + 1
        return score
    
    def getGaussianWeights(self, sigma = 5.0):
        weights = [math.exp(-math.pow(float(x)/sigma, 2.0)/2) for x in range(int(3*sigma))] # Generate Gaussian function
        min_w = min(weights)
        max_w = max(weights)
        weights = [(i-min_w)/(max_w + min_w) for i in weights] # Normalize
        return weights
    
    def getGaussianOverlap(self, idx_s, sigma = 5.0):
        """
        Gets the Gaussian Overlap of a given sentence.
        
        Args:
            idx_s : The position of sentence in the document.
            sigma : The sigma parameter for Gaussians
        
        """
        return self.getLocalOverlap(idx_s, self.getGaussianWeights(sigma))/self.sentences_[idx_s].len_
    
    def getSentenceProbability(self, s_idx):
        probability = 0
        for word in self.sentences_[s_idx].words_:
            probability += self.wordCount[word]/float(self.totalWords)
        return probability/len(self.sentences_[s_idx].words_)

    def genGO(self,sigma = 5.0):
        for i,s in enumerate(self.sentences_):
            s.go = self.getGaussianOverlap(i,sigma)
            
    def genFSO(self):
        for i,s in enumerate(self.sentences_):
            s.fso = self.getFSOverlap(s)
            
    def genFeatures(self):
        if not self.featuresGenerated :
            self.doTextRank()
            self.genFSO()
            self.genGO()
            self.featuresGenerated = True
        
    def genImportance(self,summDoc,k = 4):
        for mainSentence in self.sentences_ :
            impList = [] 
            for idx,summSentence in enumerate(summDoc.sentences_ ):
                impList.append(summSentence.similarity(mainSentence))
#                low = idx - k
#                low = max(low,0)
                
#                high = idx + k
#                high = min(high, len(summSentence))

#                imp = 0
#                for pair in itertools.combinations(summSentence.words()[low:high],2):
#                    if( pair[0] in mainSentence.words() and pair[1] in mainSentence.words()):
#                        imp += 1
#                impList.append(imp)
#                
            mainSentence.importance = max(impList)
   
    def trainMachine(self,summDoc):

        self.genFeatures()
        self.genImportance(summDoc)
        
        features = [(s.go, s.fso, s.score) for s in self.sentences_]
        impData = [s.importance for s in self.sentences_]
        
        model = SVR()
        model.fit(features, impData)
        
        return model
        
    def compress(self,machine,compression = 0.2):
        
        self.genFeatures()
        features = [(s.go, s.fso, s.score) for s in self.sentences_ ]
        prediction = machine.predict(features)
        
        sentenceSores = zip(self.sentences_,prediction)
        sortedSentences = sorted(sentenceSores, key = lambda s : s[1], reverse = True)
        
        length = int( len(self.sentences_)*compression )
        
        sortedSentences = sortedSentences[0:length]
        sortedSentences = [s[0] for s in sortedSentences]
        return sorted(sortedSentences, key = lambda x : x.index )
        
        
        
        
class Summary(Document):
    
    def __init__(self,filename,base):
        Document.__init__(self,filename)
        self.baseDoc = base
        self.generateSummaryProbability()

    def generateSummaryProbability(self):

        """
    
        Assigns the probability to each sentence in the summary exist
        given the base document.

        """
    
        for s in self.sentences_ :
            s.addCooccurProbability(self.baseDoc)

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
        




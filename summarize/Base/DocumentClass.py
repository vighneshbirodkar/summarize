import re
import os
import math
from ..Visualize.Visualizer import circleVisualize

class Document(object):
    """
    
    A class represnting a text document and all the relevant information
    
    """
    def __init__(self,fileName,_set = None):
        """
        Creates a Document object
        
        Args:
            fileName : Name of the file to use.
        
        """
        
        self._set = _set
        self._terms = set([])
        self.tf = {}
        self.idf = None
        self.tfidf = {}
        self.fileName = fileName
        with open(fileName, 'r') as f:
            for line in f:
                matchIter = re.finditer('[\w]+',line)
                for match in matchIter:
                    term = match.group().lower()
                    self._terms = self._terms.union(set([term]))
                    try :
                        self.tf[term] += 1
                    except KeyError :
                        self.tf[term] = 1
        
    def terms(self):
        """
        
        Returns the set of words in the document
        
        """
        return self._terms
        
    def getTF(self,term):
        """
        Returns term-frequency of a term 
        
        Args:
            term : The term.
            
        Returns:
            term-frequnce of term. 0 if the term is not present.
        
        """
        
        try:
            return self.tf[term]
        except KeyError :
            return 0
            
    def getIDF(self,term):
        """
        Returns inverse-dicument-frequency of a term 
        
        Args:
            term : The term.
            
        Returns:
            inverse-document-frequenct of term.
        
        Raises: 
            RuntimeError : If the parent DocumentSet is not defines
            KeyError : If the term is not presesnt
        
        """
        if self._set :
            return self._set.getIDF(term)
        else :
            raise RuntimeError("The Document does not have s Super-Set")
            
    def visualize(self):
        circleVisualize(self.tfidf)

    
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
        for name in os.listdir(directory):
            fileName = directory + os.sep + name
            doc = Document(fileName)
            doc._set = self
            self.documents.append(doc)
            self._terms = self._terms.union(doc.terms())
        
        n = len(self.documents) + 1
        
        for term in self._terms:
            count = 0.0
            for doc in self.documents :
                try :
                    doc.tf[term]
                    count += 1
                except KeyError :
                    pass
            
            self.idf[term] = math.log(n/count)
            
        min_ = 99999999999
        max_ = -999999999999
        for doc in self.documents :
            for term in self._terms :
                value = doc.getTF(term)*self.getIDF(term)
                doc.tfidf[term] = value
                
                if value > max_ :
                    max_ = value
                    
                if value < min_ :
                    min_ = value
            
            diff = max_ - min_
            for term in self._terms :
                doc.tfidf[term] = doc.tfidf[term]/diff + min_
            
    def docs(self):
        """
        Get the list of documents in the Set
        
        Returns:
            A List of Document Objects.
        
        """
        
        return self.documents
        
    def terms(self):
        """
        
        Returns the set of words in the Document Set
        
        """
        return self._terms
        
    def getIDF(self,term):
        """
        
        Returns term-frequency of a term 
        
        Args:
            term : The term.
            
        Returns:
            term-frequnce of term. 0 if the term is not present.
        
        """
        return self.idf[term]
        
        

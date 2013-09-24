import os
import webbrowser
import nltk

def circleVisualize(dataDict):
    fileName = os.path.dirname(__file__) + os.sep + 'dot.vdf'
    fil = open(fileName,"w")
    keys = dataDict.keys()
    values = [ dataDict[k] for k in keys ]
    keys = sorted(keys,key = lambda x : dataDict[x] ,reverse = True)
    tagged = nltk.pos_tag(keys)
    pruned = []
    valid = ['FW', 'JJ', 'JJR', 'JJS', 'CD', 'LS', 'MD', 'NN', 'NNS', 'NNP', 'NNPS', 'RP', 'SYM', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
    for x in tagged:
        if x[1] in valid:
            pruned.append(x[0])
    
    for key in pruned :
        fil.write(key + ',' + str(dataDict[key])  + os.linesep)
        
    fil.close()
    htmlName = os.path.dirname(__file__) + os.sep + "dot.html"
    webbrowser.open(htmlName)

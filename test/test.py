from summarize import Document
from sklearn.svm import SVR
import numpy as np

mainDoc = Document('doc.txt')
summDoc = Document('abs2.txt')

mainDoc.doTextRank()

# compute co graph
mainDoc.doCoGraph()
summDoc.addInfluenceFrom(mainDoc,1)

#for s in summDoc.sentences() :
    #co occurence prob
    #print s.getInfluence()

for i,si in enumerate( mainDoc.sentences() ):
    probs = []
    for j,sj in enumerate( summDoc.sentences() ):
        p = sj.getInfluence()*mainDoc.getSentenceProbability(i) / \
        summDoc.getSentenceProbability(j)
        probs += [p]

    si.contribProbability = max(probs)
    #print si, max(probs)
    print '\n\n\n'

sens = mainDoc.sentences()
#sens = sorted(sens, key=lambda x:x.contribProbability, reverse=True)
#for s in sens :
#    print s,s.contribProbability
#    print '\n\n\n'

feat = []
label = []

for i,sentence in enumerate(sens):
    fso = mainDoc.getFSOverlap(sentence)
    go = mainDoc.getGaussianOverlap(i)
    tr = sentence.getScore()
    feat.append((fso, go, tr))
    label.append(sentence.contribProbability)

model = SVR()
model.fit(feat, label)
predictions = []
for i in range(len(feat)):
    val = model.predict(feat[i])
    predictions.append(val[0])
ls = zip(sens, predictions)
ls = sorted(ls, key= lambda x:x[1], reverse=True)

for s,p in ls:
    print s, p
    print '\n\n\n'

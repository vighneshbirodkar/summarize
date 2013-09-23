import os

def circleVisualize(dataDict):
    fileName = os.path.dirname(__file__) + os.sep + 'data.txt'
    fil = open(fileName,"w")
    for key in dataDict :
        fil.write(key + ',' + str(dataDict[key])  + os.linesep)
        
    fil.close()

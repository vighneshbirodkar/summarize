import os
import webbrowser

def circleVisualize(dataDict):
    fileName = os.path.dirname(__file__) + os.sep + 'dot.vdf'
    fil = open(fileName,"w")
    keys = dataDict.keys()
    values = [ dataDict[k] for k in keys ]
    keys = sorted(keys,key = lambda x : dataDict[x] ,reverse = True)

    for key in keys :
        fil.write(key + ',' + str(dataDict[key])  + os.linesep)
        
    fil.close()
    htmlName = os.path.dirname(__file__) + os.sep + "dot.html"
    webbrowser.open(htmlName)

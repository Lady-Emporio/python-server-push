
import datetime
import urllib.parse

def log(*arg):
    print(datetime.datetime.now(), *arg)
    
def parseHeaders(rawMessage: str):
    headers = {}
    rawHeadersList = rawMessage.split("\r\n")
    for i in rawHeadersList:
        indexFirst = i.find(":")
        if -1 == indexFirst:
            headers[i] = ""
        else:
            key = i[:indexFirst].strip()
            val = i[indexFirst+1:].strip()
            headers[key] = val
    return headers

def getMethodPathVersion(firstLine):
    returnData = {"method":"", "path":"", "version":"", "isError": False} 
    words = firstLine.split(" ")
    if len(words)!=3:
        returnData["isError"] = True
        return returnData
    
    returnData["method"] = words[0]
    returnData["path"] = urllib.parse.unquote_plus(words[1])
    returnData["version"] = words[2]
    
    return returnData


            


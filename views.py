
import json

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import request
    
def auth(request: 'request.Request'):
    name = request.bodyParams.get("name")
    if None == name:
        request.manager.sendError(request.socket, "not 'name' body params.")
        return
    request.manager.auth(request.socket, name)
    
def getListSocket(request: 'request.Request'):
    listConnected =[]
    for key in request.manager.authSocket:
        for s in request.manager.authSocket[key]:
            listConnected.append( f"{s.fileno()}:{key}")
            
    jsonStar = json.dumps(listConnected)
    request.send_200(jsonStar)
    
def sendMessage(request: 'request.Request'):
    params = ["name","message"]
    notExistParams = []
    validParams = {}
    for param in params:
        value = request.bodyParams.get(param)
        if None == value:
            notExistParams.append(value)
        else:
            validParams[param] = value
    
    if len(notExistParams) > 0:
        request.manager.sendError(request.socket, "not valid params: " + str(notExistParams))
        return
    
    
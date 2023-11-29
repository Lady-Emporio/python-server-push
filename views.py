
import json

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import handleRequest
    
def auth(request: 'handleRequest.Request'):
    name = request.bodyParams.get("name")
    if None == name:
        request.manager.sendError(request.socket, "not 'name' body params.")
        return
    request.manager.auth(request.socket, name)
    
def getListSocket(request: 'handleRequest.Request'):
    listConnected =[]
    for key in request.manager.authSocket:
        for s in request.manager.authSocket[key]:
            listConnected.append( f"{s.fileno()}:{key}")
            
    jsonStar = json.dumps(listConnected)
    request.send_200(jsonStar)
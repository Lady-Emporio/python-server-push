
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import handleRequest
    
def auth(request: handleRequest.Request):
    name = request.bodyParams.get("name")
    if None == name:
        request.manager.sendError(request.socket, "not 'name' body params.")
        return
    request.manager.auth(request.socket, name)
    
def getListSocket(request):
    pass
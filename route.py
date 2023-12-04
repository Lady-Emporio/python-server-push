
import views

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import request

def handle_request_method_GET(request: 'request.Request'):
    if "/getlistsocket/" == request.path:
        views.getListSocket(request)
    else:
        request.manager.sendError(request.socket, "Invalid path GET.")

def handle_request_method_POST(request: 'request.Request'):
    if "/auth/" == request.path:
        views.auth(request)
    elif "/sendMessage/" == request.path:
        views.sendMessage(request)
    else:
        request.manager.sendError(request.socket, "Invalid path PATH.")
    
    

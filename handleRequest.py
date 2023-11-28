
# HTTP/1.1 404 NOT FOUND
# Server: Werkzeug/2.2.2 Python/3.11.1
# Date: Tue, 21 Nov 2023 13:26:04 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 207
# Connection: close
# Date: email.utils.formatdate(time.time(), usegmt=True)

import email.utils
import time

import socket

from clearSky import log
import urllib.parse
import views

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import main
    
class Request:
    def __init__(self, method, path: str, headers, raw_body: bytes, manager: main.ManagerSockets, socket):
        self.method = method
        self.path = path
        if not self.path.endswith("/"):
            self.path += "/"            
        self.headers = headers
        self.raw_body = raw_body
        self.manager = manager
        self.socket = socket
        self.bodyParams = {}
        
        bodyStr = self.raw_body.decode(encoding='utf-8', errors='ignore')
        rawstrBody = urllib.parse.unquote_plus(bodyStr)
        rawListBody = rawstrBody.split("&")
        for rawBodyKeyValue in rawListBody:
            indexEndKey = rawBodyKeyValue.find("=")
            self.bodyParams[rawBodyKeyValue[:indexEndKey].lower()] = rawBodyKeyValue[indexEndKey+1:]
        


def handle_request_method_GET(request: Request):
    if "/getListSocket/" == request.path:
        views.getListSocket(request)


def handle_request_method_POST(request: Request):
    if "/auth/" == request.path:
        views.auth(request)
    else:
        request.manager.sendError(request.socket, "Invalid path.")
    
    
def handle_request_method_ERROR(request: Request):
    dateStr = email.utils.formatdate(time.time(), usegmt=True)
    messageError:str = ("# HTTP/1.1 404 NOT FOUND\r\n"
                    "Server: Werkzeug/2.2.2 Python/3.11.1\r\n"
                    f"Date: {dateStr}\r\n"
                    "Content-Type: text/html; charset=utf-8\r\n"
                    "Content-Length: 0\r\n"
                    "Connection: close\r\n\r\n")
    log("handle_request_method_ERROR", "send message: ", messageError, request.socket)
    messageErrorSend = messageError.encode(encoding = "utf-8", errors = "ignore") 
    request.socket.sendall(messageErrorSend)
    request.manager.remove(socket)
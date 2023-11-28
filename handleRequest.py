
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

class Request:
    def __init__():
        pass


def handle_request_method_GET(headers, manager, socket):
    pass


def handle_request_method_POST(headers, body: bytes, manager, socket):
    bodyStr = body.decode(encoding='utf-8', errors='ignore')
    rawstrBody = urllib.parse.unquote_plus(bodyStr)
    rawListBody = rawstrBody.split("&")
    bodyMap = {}
    for rawBodyKeyValue in rawListBody:
        indexEndKey = rawBodyKeyValue.find("=")
        bodyMap[rawBodyKeyValue[:indexEndKey].lower()] = rawBodyKeyValue[indexEndKey+1:]
    print("handle_request_method_POST body", bodyMap)
    
    #if bodyMap["auth"]
    
    
def handle_request_method_ERROR(manager, socket: socket.socket):
    dateStr = email.utils.formatdate(time.time(), usegmt=True)
    messageError:str = ("# HTTP/1.1 404 NOT FOUND\r\n"
                    "Server: Werkzeug/2.2.2 Python/3.11.1\r\n"
                    f"Date: {dateStr}\r\n"
                    "Content-Type: text/html; charset=utf-8\r\n"
                    "Content-Length: 0\r\n"
                    "Connection: close\r\n\r\n")
    log("handle_request_method_ERROR", "send message: ",messageError, socket)
    messageErrorSend = messageError.encode(encoding = "utf-8", errors = "ignore") 
    socket.sendall(messageErrorSend)
    manager.remove(socket)
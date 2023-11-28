import socket
import select
import typing

from clearSky import log
import clearSky
from handleRequest import (handle_request_method_GET, handle_request_method_POST,
                           handle_request_method_ERROR)
HOST, PORT = "127.0.0.1", 8001

class ManagerSockets:
    _instance = None

    allSockets: typing.List[socket.socket] = []
    authSocket: typing.Dict[str, typing.List[socket.socket]] = {}  # Name: list socket
    socketMessages: typing.Dict[socket.socket, bytes] = {}
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance

    def append(self, socket):
        self.allSockets.append(socket)

    def remove(self, socket: socket.socket):
        for key in self.authSocket:
            socketList = self.authSocket[key]
            while socketList.count(socket):
                socketList.remove(socket)
                log("remove auth: ", key, socket)
        self.allSockets.remove(socket)
        log("remove from all sockets: ", socket)
        
        testExist = self.socketMessages.get(socket)
        if None != testExist:
            log("WARRING.", "remove", "exist message: ", testExist)
        socket.close()
    
    def addMessage(self, socket: socket.socket, message: bytes):
        self.socketMessages[socket] = self.socketMessages.get(socket, b'') + message
        
    def parseMessage(self, socket: socket.socket):
        splitPart = b'\r\n\r\n'
        message = self.socketMessages.get(socket, b'')
        indexEndHeader = message.find(splitPart)
        if -1 == indexEndHeader:
            log(b"parseMessage. come part message: " + message)
            return
        headersBytes = message [:indexEndHeader]
        log("headersBytes:", headersBytes)
        anotherPart = message[indexEndHeader+len(splitPart):]
        messageLast = anotherPart
        
        strMessageLower = headersBytes.decode(encoding='utf-8', errors='ignore').lower()
        indexEndFirstLine = strMessageLower.find("\r\n")
        if -1 == indexEndFirstLine:
            log("ERROR")
            self.remove(socket)
            return
        strFirstLine = strMessageLower[:indexEndFirstLine]
        headersAfterHeadersLine = strMessageLower[indexEndFirstLine+len("\r\n"): ]
        methodPathVersion = clearSky.getMethodPathVersion(strFirstLine)
        headers = clearSky.parseHeaders(headersAfterHeadersLine)
        
        if 0 == len(headers):
            log("ERROR")
            self.remove(socket)
            return
        
        method,path,version = methodPathVersion["method"], methodPathVersion["path"], methodPathVersion["version"]
        log("method: ", method, "path: ", path, "version: ", version)
        if "get" == method:
            handle_request_method_GET(headers, self, socket)  
        elif "post" == method:
            try:
                content_length = int(headers.get("content-length", 0))
            except ValueError:
                content_length = 0
            body = anotherPart[0:content_length]
            messageLast = anotherPart[content_length:]
            handle_request_method_POST(headers, body, self, socket)
        else:
            handle_request_method_ERROR(self, socket)
            
        log("parseMessage. MessageLast:", messageLast)
        self.socketMessages[socket] = messageLast
       
    def auth(self, socket: socket.socket, name: str):
        s_list = self.authSocket.setdefault(name, [])
        s_list.append(socket)

def workWithSocket(socket : socket.socket, manager: ManagerSockets):
    allData = b''
    timeout = 0
    log("Begin recv", socket)
    while True:
        readable, writeable, exceptional = select.select([socket], [], [], timeout)
        if 0 == len(readable):
            log("recv from", socket, allData)
            break
        log("Before recv", socket)
        try:
            data = socket.recv(1024)
        except ConnectionError:
            log("connection close by client", socket)
            manager.remove(socket)
            break
        log("After recv", socket, data)
        
        if b'' == data:
            log("connection close", socket)
            manager.remove(socket)
            break
        allData += data
    
    if b'' == allData:
        log("its message about close", socket)
        return
    
    log("work with: ", allData)
    manager.addMessage(socket, allData)
    manager.parseMessage(socket)

def serverForever():
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sock.bind((HOST, PORT))
    serv_sock.listen(10)

    timeout = 5
    manager = ManagerSockets()
    while True:
        rlist = manager.allSockets + [serv_sock]
        log("rlist", rlist)
        readable, writeable, exceptional = select.select(rlist, [], [], timeout)
        for sock in readable:
            if sock == serv_sock:
                sock, addr = serv_sock.accept()
                log("Connected by", addr)
                manager.append(sock)
            else:
                workWithSocket(sock, manager)


serverForever()

import socket as ssocket
import select
import typing

from clearSky import log
import clearSky
from request import Request
import route

HOST, PORT = "127.0.0.1", 8001
NOT_AUTH_GROUP = ""
class ManagerSockets:
    _instance = None

    allSockets: typing.List[ssocket.socket] = []
    authSocket: typing.Dict[str, typing.List[ssocket.socket]] = {}  # Name: list socket
    socketMessages: typing.Dict[ssocket.socket, bytes] = {}
    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def append(self, socket: ssocket.socket):
        self.allSockets.append(socket)
        s_list = self.authSocket.setdefault(NOT_AUTH_GROUP, [])
        s_list.append(socket)

    def remove(self, socket: ssocket.socket):
        for key in self.authSocket:
            socket_list = self.authSocket[key]
            while socket_list.count(socket)>0:
                socket_list.remove(socket)
                log("remove auth: ", key, socket)
        self.allSockets.remove(socket)
        log("remove from all sockets: ", socket)
        
        test_exist = self.socketMessages.get(socket)
        if None != test_exist and b"" != test_exist:
            log("WARRING.", "remove", "exist message: ", test_exist)
        socket.close()
    
    def addMessage(self, socket: ssocket.socket, message: bytes):
        self.socketMessages[socket] = self.socketMessages.get(socket, b'') + message
        
    def parseMessage(self, socket: ssocket.socket):
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

        raw_body = b""
        if "post" == method:
            try:
                content_length = int(headers.get("content-length", 0))
            except ValueError:
                content_length = 0
            raw_body = anotherPart[0:content_length]
            messageLast = anotherPart[content_length:]
            
        request = Request(method, path, headers, raw_body, self, socket)
        if "get" == method:
            route.handle_request_method_GET(request)  
        elif "post" == method:
            route.handle_request_method_POST(request)
        else:
            request.send_bad_request_400(f"method not get and not post: '{method}'.")
            
        log("parseMessage. MessageLast:", messageLast)
        self.socketMessages[socket] = messageLast
       
    def auth(self, socket: ssocket.socket, name: str):
        log("auth: ", name, "socket: ", socket)
        not_auth_list = self.authSocket.setdefault(NOT_AUTH_GROUP, [])
        if not_auth_list.count(socket)>0:
            not_auth_list.remove(socket)
        s_list = self.authSocket.setdefault(name, [])
        s_list.append(socket)

        
def workWithSocket(socket : ssocket.socket, manager: ManagerSockets):
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
    serv_sock = ssocket.socket(ssocket.AF_INET, ssocket.SOCK_STREAM)
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

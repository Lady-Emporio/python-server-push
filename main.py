import socket as lib_socket
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

    allSockets: typing.List[lib_socket.socket] = []
    authSocket: typing.Dict[str, typing.List[lib_socket.socket]] = {}  # Name: list socket
    socketMessages: typing.Dict[lib_socket.socket, bytes] = {}

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
        return cls._instance

    def append(self, socket: lib_socket.socket):
        self.allSockets.append(socket)
        s_list = self.authSocket.setdefault(NOT_AUTH_GROUP, [])
        s_list.append(socket)

    def remove(self, socket: lib_socket.socket):
        for key in self.authSocket:
            socket_list = self.authSocket[key]
            while socket_list.count(socket) > 0:
                socket_list.remove(socket)
                log("remove auth: ", key, socket)
        self.allSockets.remove(socket)
        log("remove from all sockets: ", socket)

        test_exist = self.socketMessages.get(socket)
        if test_exist is not None and b"" != test_exist:
            log("WARRING.", "remove", "exist message: ", test_exist)
        socket.close()

    def add_message(self, socket: lib_socket.socket, message: bytes):
        self.socketMessages[socket] = self.socketMessages.get(socket, b'') + message

    def parse_message(self, socket: lib_socket.socket):
        split_part = b'\r\n\r\n'
        message = self.socketMessages.get(socket, b'')
        index_end_header = message.find(split_part)
        if -1 == index_end_header:
            log(b"parseMessage. come part message: " + message)
            return
        headers_bytes = message[:index_end_header]
        log("headers_bytes: ", headers_bytes)
        another_part = message[index_end_header + len(split_part):]
        message_last = another_part

        str_message_lower = headers_bytes.decode(encoding='utf-8', errors='ignore').lower()
        index_end_first_line = str_message_lower.find("\r\n")
        if -1 == index_end_first_line:
            log("ERROR")
            self.remove(socket)
            return
        str_first_line = str_message_lower[:index_end_first_line]
        headers_after_headers_line = str_message_lower[index_end_first_line + len("\r\n"):]
        method_path_version = clearSky.get_method_path_version(str_first_line)
        headers = clearSky.parse_headers(headers_after_headers_line)

        if 0 == len(headers):
            log("ERROR")
            self.remove(socket)
            return

        method, path, version = (method_path_version["method"],
                                 method_path_version["path"],
                                 method_path_version["version"])
        log("method: ", method, "path: ", path, "version: ", version)

        raw_body = b""
        if "post" == method:
            try:
                content_length = int(headers.get("content-length", 0))
            except ValueError:
                content_length = 0
            raw_body = another_part[0:content_length]
            message_last = another_part[content_length:]

        request = Request(method, path, headers, raw_body, self, socket)
        if "get" == method:
            route.handle_request_method_GET(request)
        elif "post" == method:
            route.handle_request_method_POST(request)
        else:
            request.send_bad_request_400(f"method not get and not post: '{method}'.")

        log("parseMessage. MessageLast:", message_last)
        self.socketMessages[socket] = message_last

    def auth(self, socket: lib_socket.socket, name: str):
        log("auth: ", name, "socket: ", socket)
        not_auth_list = self.authSocket.setdefault(NOT_AUTH_GROUP, [])
        if not_auth_list.count(socket) > 0:
            not_auth_list.remove(socket)
        s_list = self.authSocket.setdefault(name, [])
        s_list.append(socket)


def work_with_socket(socket: lib_socket.socket, manager: ManagerSockets):
    all_data = b''
    timeout = 0
    log("Begin recv", socket)
    while True:
        readable, writeable, exceptional = select.select([socket], [], [], timeout)
        if 0 == len(readable):
            log("recv from", socket, all_data)
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
        all_data += data

    if b'' == all_data:
        log("its message about close", socket)
        return

    log("work with: ", all_data)
    manager.add_message(socket, all_data)
    manager.parse_message(socket)


def server_forever():
    serv_sock = lib_socket.socket(lib_socket.AF_INET, lib_socket.SOCK_STREAM)
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
                work_with_socket(sock, manager)


server_forever()

# HTTP/1.1 404 NOT FOUND
# Server: Werkzeug/2.2.2 Python/3.11.1
# Date: Tue, 21 Nov 2023 13:26:04 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 207
# Connection: close
# Date: email.utils.formatdate(time.time(), usegmt=True)

import email.utils
import time

import socket as lib_socket

from clearSky import log
import urllib.parse

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import main

# success
OK = 200, 'OK'
# client error
BAD_REQUEST = 400, 'Bad Request'
NOT_FOUND = 404, 'Not Found'
# server errors
INTERNAL_SERVER_ERROR = 500, 'Internal Server Error'


class Request:
    def __init__(self,  method: str, path: str, headers,
                 raw_body: bytes, manager: 'main.ManagerSockets', socket: lib_socket.socket):
        self.method = method
        self.path = path
        if not self.path.endswith("/"):
            self.path += "/"
        self.headers = headers
        self.raw_body = raw_body
        self.manager = manager
        self.socket = socket
        self.bodyParams = {}

        body_str = self.raw_body.decode(encoding='utf-8', errors='ignore')
        raw_str_body = urllib.parse.unquote_plus(body_str)
        raw_list_body = raw_str_body.split("&")
        for rawBodyKeyValue in raw_list_body:
            index_end_key = rawBodyKeyValue.find("=")
            self.bodyParams[rawBodyKeyValue[:index_end_key].lower()] = rawBodyKeyValue[index_end_key + 1:]

    def send_200(self, body: str):
        self.__send(body, OK)

    def send_not_found_404(self, body: str):
        self.__send(body, NOT_FOUND)

    def send_bad_request_400(self, body: str):
        self.__send(body, BAD_REQUEST)

    def __send(self, body: str, code: tuple[int,str]):
        body_bytes = body.encode('UTF-8', 'replace')
        content_length = str(len(body))

        date_str = email.utils.formatdate(time.time(), usegmt=True)
        message_text: str = (f"HTTP/1.1 {code[0]} {code[1]}\r\n"
                             "Server: Lady-Emporio\r\n"
                             f"Date: {date_str}\r\n"
                             "Content-Type: text/html; charset=utf-8\r\n"
                             f"Content-Length: {content_length}\r\n"
                             "Connection: keep-alive\r\n\r\n")
        message = message_text.encode(encoding="utf-8", errors='replace')
        message += body_bytes
        log("send_200", message)
        self.socket.sendall(message)

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

# success
OK = 200, 'OK'
# client error
BAD_REQUEST = 400, 'Bad Request'
NOT_FOUND = 404, 'Not Found'
# server errors
INTERNAL_SERVER_ERROR = 500, 'Internal Server Error'


class Request:
    def __init__(self, method, path: str, headers, raw_body: bytes, manager: 'main.ManagerSockets', socket):
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
        rawStrBody = urllib.parse.unquote_plus(bodyStr)
        rawListBody = rawStrBody.split("&")
        for rawBodyKeyValue in rawListBody:
            indexEndKey = rawBodyKeyValue.find("=")
            self.bodyParams[rawBodyKeyValue[:indexEndKey].lower()] = rawBodyKeyValue[indexEndKey + 1:]

    def send_200(self, body: str):
        self.__send(body, OK[1])

    def send_not_found_404(self, body: str):
        self.__send(body, NOT_FOUND[1])

    def send_bad_request_400(self, body: str):
        self.__send(body, BAD_REQUEST[1])

    def __send(self, body: str, code: str):
        body_bytes = body.encode('UTF-8', 'replace')
        content_length = str(len(body))

        date_str = email.utils.formatdate(time.time(), usegmt=True)
        message_text: str = (f"HTTP/1.1 {code}\r\n"
                             "Server: Lady-Emporio\r\n"
                             f"Date: {date_str}\r\n"
                             "Content-Type: text/html; charset=utf-8\r\n"
                             f"Content-Length: {content_length}\r\n"
                             "Connection: keep-alive\r\n\r\n")
        message = message_text.encode(encoding="utf-8", errors='replace')
        message += body_bytes
        log("send_200", message)
        self.socket.sendall(message)

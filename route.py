import views

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import request as lib_request


def handle_request_method_GET(request: 'lib_request.Request'):
    if "/getlistsocket/" == request.path:
        views.getListSocket(request)
    else:
        request.send_not_found_404("Invalid path GET.")


def handle_request_method_POST(request: 'lib_request.Request'):
    if "/auth/" == request.path:
        views.auth(request)
    elif "/sendMessage/" == request.path:
        views.sendMessage(request)
    else:
        request.send_not_found_404("Invalid path PATH.")

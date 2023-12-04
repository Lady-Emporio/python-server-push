import json

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import request as lib_request


def auth(request: 'lib_request.Request'):
    name = request.bodyParams.get("name")
    if name is None:
        request.send_bad_request_400("not 'name' body params.")
        return
    request.manager.auth(request.socket, name)


def getListSocket(request: 'lib_request.Request'):
    listConnected = []
    for key in request.manager.authSocket:
        for s in request.manager.authSocket[key]:
            listConnected.append(f"{s.fileno()}:{key}")

    jsonStar = json.dumps(listConnected)
    request.send_200(jsonStar)


def sendMessage(request: 'lib_request.Request'):
    params = ["name", "message"]
    not_exist_params = []
    valid_params = {}
    for param in params:
        value = request.bodyParams.get(param)
        if value is None:
            not_exist_params.append(value)
        else:
            valid_params[param] = value

    if len(not_exist_params) > 0:
        request.send_bad_request_400("not valid params: " + str(not_exist_params))
        return

import datetime
import urllib.parse


def log(*arg):
    print(datetime.datetime.now(), *arg)


def parse_headers(raw_message: str):
    headers = {}
    raw_headers_list = raw_message.split("\r\n")
    for i in raw_headers_list:
        index_first = i.find(":")
        if -1 == index_first:
            headers[i] = ""
        else:
            key = i[:index_first].strip()
            val = i[index_first + 1:].strip()
            headers[key] = val
    return headers


def get_method_path_version(first_line):
    return_data = {"method": "", "path": "", "version": "", "isError": False}
    words = first_line.split(" ")
    if len(words) != 3:
        return_data["isError"] = True
        return return_data

    return_data["method"] = words[0]
    return_data["path"] = urllib.parse.unquote_plus(words[1])
    return_data["version"] = words[2]

    return return_data

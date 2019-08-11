"""
Module for misc functions interacting with the telgram api
"""
import json

import urllib.parse
import urllib.request


API_URL = None


def resolve_ids_to_names(ids, gid):
    url = "{}/getChatMember".format(API_URL)
    names = []
    for uid in ids:
        data = {
            "chat_id": gid,
            "user_id": uid
        }
        data = urllib.parse.urlencode(data)
        data = data.encode('ascii')  # data should be bytes
        req = urllib.request.Request(url, data)
        with urllib.request.urlopen(req) as response:
            the_page = response.read()
            responseData = json.loads(the_page)["result"]
            names.append(responseData["user"].get("username") or "{} {}".format(responseData["user"].get("first_name"), responseData["user"].get("last_name")))
    return dict(zip(ids, names))


def call_method(method, payload):
    url = "{}/{}".format(API_URL, method)
    data = urllib.parse.urlencode(payload)
    data = data.encode('ascii')
    req = urllib.request.Request(url, data)
    with urllib.request.urlopen(req) as response:
        the_page = response.read()
        responseData = json.loads(the_page)["result"]
        return responseData

import json

from django.shortcuts import get_object_or_404

from apps.users.models import User
from apps.users.services import UserService


class ClientRequest:
    def __init__(self, client):
        self.client = client

    def __call__(self, type, url, data=None):
        content_type = "application/json"
        accept_header = "application/json;"

        if type == "get":
            res = self.client.get(
                url,
                {},
                content_type=content_type,
                HTTP_ACCEPT=accept_header,
            )
        elif type == "post":
            res = self.client.post(
                url,
                json.dumps(data),
                content_type=content_type,
                HTTP_ACCEPT=accept_header,
            )
        elif type == "del":
            res = self.client.delete(
                url,
                {},
                content_type=content_type,
                HTTP_ACCEPT=accept_header,
            )
        elif type == "put":
            res = self.client.put(
                url,
                json.dumps(data),
                content_type=content_type,
                HTTP_ACCEPT=accept_header,
            )
        else:
            res = self.client.patch(
                url,
                json.dumps(data),
                content_type=content_type,
                HTTP_ACCEPT=accept_header,
            )
        return res

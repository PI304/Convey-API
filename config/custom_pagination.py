from collections import OrderedDict

from rest_framework import pagination
from rest_framework.response import Response


class CustomPagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    page_query_param = "page"

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("total_count", self.page.paginator.count),
                    ("total_page_count", self.page.paginator.count // 20 + 1),
                    ("page_size", self.page_size),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "total_count": {
                    "type": "integer",
                    "example": 123,
                },
                "total_page_count": {
                    "type": "integer",
                    "example": 12,
                },
                "page_size": {
                    "type": "integer",
                    "example": 20,
                },
                "next": {
                    "type": "string",
                    "nullable": True,
                    "format": "uri",
                    "example": f"http://api.example.org/accounts/?{self.page_query_param}=2",
                },
                "previous": {
                    "type": "string",
                    "nullable": True,
                    "format": "uri",
                    "example": f"http://api.example.org/accounts/?{self.page_query_param}=2",
                },
                "results": schema,
            },
        }

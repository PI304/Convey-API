from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.inspectors import PaginatorInspector


class CustomPaginationInspector(PaginatorInspector):
    def get_paginated_response(self, paginator, response_schema):
        """
        :param BasePagination paginator: the paginator
        :param openapi.Schema response_schema: the response schema that must be paged.
        :rtype: openapi.Schema
        """

        return openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=OrderedDict(
                (
                    ("total_count", openapi.Schema(type=openapi.TYPE_INTEGER)),
                    ("total_page_count", openapi.Schema(type=openapi.TYPE_INTEGER)),
                    (
                        "next",
                        openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_URI,
                            x_nullable=True,
                        ),
                    ),
                    (
                        "previous",
                        openapi.Schema(
                            type=openapi.TYPE_STRING,
                            format=openapi.FORMAT_URI,
                            x_nullable=True,
                        ),
                    ),
                    ("results", response_schema),
                )
            ),
            required=["results"],
        )

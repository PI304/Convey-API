from typing import Any

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.request import Request
from rest_framework.response import Response


class SurveyPackageAnswerListView(generics.CreateAPIView):
    @swagger_auto_schema(
        tags=["survey-answer"],
        operation_summary="해당 survey 에 대한 피험자의 응답을 생성합니다",
        operation_description="헤더의 Authorization 를 이용하여 앱 이용자임을 식별합니다. 피험자 id 는 request body 에 명시합니다\n피험자 응답은 Part 단위로 생성하며 sector 에 대한 응답들로 리스트가 구성됩니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "subject_id": openapi.Schema(
                    type=openapi.TYPE_STRING, description="피험자 고유 id"
                ),
                "sectors": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "sector_id": openapi.Schema(
                                type=openapi.TYPE_INTEGER, description="sector id"
                            ),
                            "answers": openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                description="문항 응답을 순서대로 리스트에 담습니다",
                                items=openapi.Schema(
                                    description="문항 응답 (숫자 or 문자)",
                                    type=openapi.TYPE_INTEGER,
                                ),
                            ),
                        },
                    ),
                ),
            },
        ),
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        pass


class SurveyPackageAnswerDetailView(generics.RetrieveUpdateDestroyAPIView):
    pass

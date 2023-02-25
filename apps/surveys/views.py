from typing import Any

from django.shortcuts import render
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.request import Request
from rest_framework.response import Response

from apps.surveys.models import SurveySector


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="요청을 보내는 유저가 만든 모든 survey 를 가져옵니다",
    ),
)
class SurveyListView(generics.ListCreateAPIView):
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="다수의 sector 로 구성된 small survey 를 만듭니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            description="sector 로 구성된 list",
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                description="하나의 sector, 문제 유형에 따라 구분됩니다",
                properties={
                    "description": openapi.Schema(
                        type=openapi.TYPE_STRING, description="sector 에 더해질 설명"
                    ),
                    "question_type": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description=f"가능한 타입은 {str(SurveySector.QuestionType.choices)}",
                    ),
                    "choices": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        description="해당 섹터의 선지 구성에 대한 정보 (선지가 다섯개라면 다섯개의 element 가 있어야 합니다)",
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "key": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="문제 유형에 따른 key-value 값 구성은 리드미 참고",
                                ),
                                "value": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="문제 유형에 따른 key-value 값 구성은 리드미 참고",
                                ),
                            },
                        ),
                    ),
                    "questions": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        description="실제 문항 list",
                        items=openapi.Schema(
                            type=openapi.TYPE_STRING, description="실제 문항 내용"
                        ),
                    ),
                },
            ),
        ),
    )
    def post(self, request, *args, **kwargs):
        pass


class SurveyDetailView(generics.RetrieveUpdateDestroyAPIView):
    allowed_methods = ["PUT", "GET", "DELETE"]

    @swagger_auto_schema(
        operation_summary="survey의 하위 sector 들을 모두 가져옵니다",
    )
    def get(self, request, *args, **kwargs):
        pass

    @swagger_auto_schema(
        operation_summary="설문을 수정합니다. 기존의 설문은 삭제되고 새롭게 생성됩니다",
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, description="POST 와 동일"),
        responses={
            400: "No cookies attached",
            409: "Verification code does not match",
        },
    )
    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # TODO: 관련된 sector 다 지우고 새로 생성
        # return HttpResponseRedirect()
        pass

    @swagger_auto_schema(
        operation_summary="설문 패키지를 완전히 삭제합니다. 관련된 모든 데이터들이 삭제됩니다",
        responses={
            400: "No cookies attached",
            409: "Verification code does not match",
        },
    )
    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        pass

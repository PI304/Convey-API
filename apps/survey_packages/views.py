from typing import Any

from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, mixins
from rest_framework.request import Request
from rest_framework.response import Response


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="요청을 보내는 유저가 만든 모든 survey package 를 가져옵니다",
    ),
)
class SurveyPackageListView(generics.ListCreateAPIView):
    @swagger_auto_schema(
        operation_summary="하나의 설문 패키지를 만듭니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "workspaceId": openapi.Schema(
                        type=openapi.TYPE_INTEGER, description="workspace ID"
                    ),
                    "title": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="PART (디바이더) 의 이름",
                    ),
                    "subjects": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        description="디바이더 (PART) 아래 주제",
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "title": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="디바이더 아래의 주제 이름",
                                ),
                                "surveys": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    description="연결할 survey ID들",
                                    items=openapi.Schema(
                                        type=openapi.TYPE_INTEGER,
                                        description="survey id",
                                    ),
                                ),
                            },
                        ),
                    ),
                },
            ),
        ),
        responses={
            400: "No cookies attached",
            409: "Verification code does not match",
        },
    )
    def post(self, request, *args, **kwargs):
        pass

    def list(self, request, *args, **kwargs):
        pass


class SurveyPackageDetailView(generics.RetrieveUpdateDestroyAPIView):
    allowed_methods = ["PUT", "DELETE", "GET"]

    @swagger_auto_schema(
        operation_summary="하나의 패키지 안에 있는 모든 Parts 를 가져옵니다",
        responses={
            400: "No cookies attached",
            409: "Verification code does not match",
        },
    )
    def get(self, request, *args, **kwargs):
        pass

    @swagger_auto_schema(
        operation_summary="설문 패키지를 수정합니다. 기존의 설문 패키지는 삭제되고 새롭게 생성됩니다",
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, description="POST 와 동일"),
        responses={
            400: "No cookies attached",
            409: "Verification code does not match",
        },
    )
    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # TODO: 관련된 parts 다 지우고 새로 생성
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

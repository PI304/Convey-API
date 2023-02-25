from typing import Any

from django.shortcuts import render
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, mixins
from rest_framework.request import Request
from rest_framework.response import Response


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="요청을 보내는 유저의 모든 workspace 를 가져옵니다",
    ),
)
class WorkspaceListView(generics.ListCreateAPIView):
    def list(self, request, *args, **kwargs):
        pass

    @swagger_auto_schema(
        operation_summary="빈 workspace 를 생성합니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="워크스페이스 이름"
                )
            },
        ),
    )
    def post(self, request, *args, **kwargs):
        pass


@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        operation_summary="설문 패키지를 완전히 삭제합니다. 관련된 모든 데이터들이 삭제됩니다",
        responses={
            400: "No cookies attached",
            409: "Verification code does not match",
        },
    ),
)
class WorkspaceDestroyView(generics.DestroyAPIView):
    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        pass


class RoutineView(generics.RetrieveAPIView, generics.CreateAPIView):
    @swagger_auto_schema(
        operation_summary="해당 workspace id 의 루틴을 가져옵니다",
    )
    def get(self, request: Request, *args: Any, **kwargs) -> Response:
        pass

    @swagger_auto_schema(
        operation_summary="workspace 에 대응하는 루틴을 만듭니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "kick_off": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="kick off survey 의 id"
                ),
                "routines": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="루틴의 시작은 킥오프 서베이를 수행한 다음날을 기준으로 합니다",
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "nth_day": openapi.Schema(
                                type=openapi.TYPE_INTEGER, description="n번째 날"
                            ),
                            "time": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="설문에 응답할 시간, HH:MM 포맷",
                            ),
                            "survey_id": openapi.Schema(
                                type=openapi.TYPE_INTEGER, description="응답할 설문의 id"
                            ),
                        },
                    ),
                ),
            },
        ),
    )
    def post(self, request: Request, *args: Any, **kwargs) -> Response:
        pass

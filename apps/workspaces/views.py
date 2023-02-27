from typing import Any

from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response

from apps.survey_packages.models import SurveyPackage
from apps.workspaces.models import Workspace, Routine, RoutineDetail
from apps.workspaces.serializers import (
    WorkspaceSerializer,
    RoutineSerializer,
    RoutineDetailSerializer,
)
from apps.workspaces.services import RoutineService
from config.exceptions import InstanceNotFound


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="요청을 보내는 유저의 모든 workspace 를 가져옵니다",
    ),
)
class WorkspaceListView(generics.ListCreateAPIView):
    pagination_class = None
    serializer_class = WorkspaceSerializer
    queryset = Workspace.objects.all()

    def get_queryset(self) -> QuerySet:
        return self.queryset.filter(owner_id=self.request.user.id)

    @swagger_auto_schema(
        operation_summary="빈 workspace 를 생성합니다",
        request_body=openapi.Schema(
            required=["name", "access_code"],
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="워크스페이스 이름",
                ),
                "accessCode": openapi.Schema(
                    type=openapi.TYPE_STRING, description="워크스페이스의 비밀번호"
                ),
            },
        ),
        responses={200: openapi.Response("created", WorkspaceSerializer)},
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exceptions=True):
            serializer.save(owner_id=request.user.id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        operation_summary="워크스페이스를 삭제합니다. 관련된 루틴도 삭제됩니다",
        responses={
            400: "No cookies attached",
            409: "Verification code does not match",
        },
    ),
)
class WorkspaceDestroyView(generics.DestroyAPIView):
    serializer_class = WorkspaceSerializer
    queryset = Workspace.objects.all()


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="해당 workspace id 의 루틴을 가져옵니다",
    ),
)
class RoutineView(generics.RetrieveAPIView, generics.CreateAPIView):
    serializer_class = RoutineSerializer
    queryset = Routine.objects.all()

    def get_queryset(self) -> QuerySet:
        return self.queryset.select_related("routine_details")

    def get_object(self) -> Routine:
        return self.queryset.filter(workspace_id=self.kwargs.get("pk")).first()

    @swagger_auto_schema(
        operation_summary="workspace 에 대응하는 루틴을 만듭니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "duration": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="킥오프 서베이 이후부터의 루틴 날짜 수"
                ),
                "kick_off": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="kick off survey package 의 id",
                ),
                "routines": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="서베이를 수행한 다음날부터의 루틴입니다",
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
                            "survey_package": openapi.Schema(
                                type=openapi.TYPE_INTEGER, description="응답할 설문 패키지의 id"
                            ),
                        },
                    ),
                ),
            },
        ),
        responses={
            201: openapi.Response("ok", RoutineSerializer),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs) -> Response:
        kick_off_package_id = request.data.get("kick_off")

        try:
            kick_off_package = get_object_or_404(SurveyPackage, id=kick_off_package_id)
        except Http404:
            raise InstanceNotFound(
                "survey package allocated for kick-off survey does not exist"
            )

        data = dict(
            kick_off=kick_off_package, duration=request.data.get("duration", None)
        )

        # Create Routine
        routine_serializer = self.get_serializer(data=data)

        if routine_serializer.is_valid(raise_exceptions=True):
            routine_serializer.save(workspace_id=kwargs.get("pk"))

        routine_service = RoutineService(routine_serializer.data.get("id"))

        # Create Routine Details
        routine_details = request.data.get("routines", None)
        if routine_details:
            routine = routine_service.add_routine_details(routine_details)
            return Response(
                self.get_serializer(routine), status=status.HTTP_201_CREATED
            )
        else:
            return Response(routine_serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        operation_summary="루틴에 세부 일정을 추가합니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "nth_day": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="n번째 날"
                ),
                "time": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="설문에 응답할 시간, HH:MM 포맷",
                ),
                "survey_package": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="응답할 설문 패키지의 id"
                ),
            },
        ),
    ),
)
class RoutineDetailCreateView(generics.CreateAPIView):
    serializer_class = RoutineDetailSerializer
    queryset = RoutineDetail.objects.all()

    def perform_create(self, serializer):
        serializer.save(
            routine_id=self.request.data.get("routine_id", None),
            survey_package_id=self.request.data.get("survey_package", None),
        )


@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        operation_summary="루틴의 세부 일정을 삭제합니다",
    ),
)
class RoutineDetailView(generics.DestroyAPIView):
    queryset = RoutineDetail.objects.all()
    serializer_class = RoutineDetailSerializer

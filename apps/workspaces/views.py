from typing import Any

import shortuuid
from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.generics import get_object_or_404 as _get_object_or_404
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from apps.survey_packages.models import SurveyPackage
from apps.workspaces.models import (
    Workspace,
    Routine,
    RoutineDetail,
    WorkspaceComposition,
)
from apps.workspaces.serializers import (
    WorkspaceSerializer,
    RoutineSerializer,
    RoutineDetailSerializer,
)
from apps.workspaces.services import RoutineService, WorkspaceService
from config.exceptions import InstanceNotFound
from config.permissions import IsOwnerOrReadOnly


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
        return (
            self.queryset.filter(owner_id=self.request.user.id)
            .select_related("owner")
            .prefetch_related("survey_packages")
        )

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
        if serializer.is_valid(raise_exception=True):
            serializer.save(owner_id=request.user.id, uuid=shortuuid.uuid())

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="해당 id 의 workspace 를 가져옵니다",
        responses={200: openapi.Response("ok", WorkspaceSerializer)},
    ),
)
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
class WorkspaceDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = WorkspaceSerializer
    queryset = Workspace.objects.all()

    def get_queryset(self) -> QuerySet:
        return (
            self.queryset.filter(owner_id=self.request.user.id)
            .select_related("owner")
            .prefetch_related("survey_packages")
        )


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="해당 workspace id 의 루틴을 가져옵니다",
    ),
)
class RoutineView(generics.RetrieveAPIView, generics.CreateAPIView):
    serializer_class = RoutineSerializer
    queryset = Routine.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self) -> QuerySet:
        return self.queryset.select_related("workspace").prefetch_related(
            "workspace__owner", "routines"
        )

    def get_object(self) -> Routine:
        return _get_object_or_404(
            self.get_queryset(), workspace_id=self.kwargs.get("pk")
        )

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

        data = dict(duration=request.data.get("duration", None))

        # Create Routine
        routine_serializer = self.get_serializer(data=data)

        if routine_serializer.is_valid(raise_exception=True):
            routine_serializer.save(
                workspace_id=kwargs.get("pk"),
                kick_off_id=kick_off_package_id,
            )

        routine_service = RoutineService(routine_serializer.data.get("id"))

        # Create Routine Details
        routine_details = request.data.get("routines", None)
        if routine_details:
            routine = routine_service.add_routine_details(routine_details)
            routine.refresh_from_db()
            return Response(
                self.get_serializer(routine).data, status=status.HTTP_201_CREATED
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
                "routine": openapi.Schema(
                    type=openapi.TYPE_STRING, description="전체 루틴의 id"
                ),
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
            routine_id=self.request.data.get("routine", None),
            survey_package_id=self.request.data.get("survey_package", None),
        )


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="id 에 따라 루틴의 세부 일정을 가져옵니다",
    ),
)
@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        operation_summary="루틴의 세부 일정을 삭제합니다",
    ),
)
class RoutineDetailView(generics.RetrieveDestroyAPIView):
    queryset = RoutineDetail.objects.all()
    serializer_class = RoutineDetailSerializer


class WorkspaceAddSurveyPackageView(generics.CreateAPIView):
    queryset = Workspace.objects.all()
    serializer_class = WorkspaceSerializer

    @swagger_auto_schema(
        operation_summary="워크스페이스에 설문 패키지를 추가합니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "survey_packages": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="추가하고 싶은 모든 survey package 들의 id",
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                )
            },
        ),
        responses={201: openapi.Response("created", WorkspaceSerializer)},
    )
    def post(self, request: Request, *args: Any, **kwargs) -> Response:
        try:
            workspace = get_object_or_404(Workspace, id=kwargs.get("pk", None))
        except Http404:
            raise InstanceNotFound("no workspace by the provided id")

        survey_package_ids = request.data.get("survey_packages")
        if type(survey_package_ids) != list:
            raise ValidationError("'survey_packages' must be an array")

        service = WorkspaceService(workspace)
        workspace = service.add_survey_packages(survey_package_ids)

        serializer = self.get_serializer(workspace)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WorkspaceDestroySurveyPackageView(generics.DestroyAPIView):
    queryset = WorkspaceComposition.objects.all()
    serializer_class = WorkspaceSerializer

    def get_queryset(self) -> QuerySet:
        return self.queryset.filter(survey_package_id=self.kwargs.get("pk"))

    @swagger_auto_schema(
        operation_summary="워크스페이스에서 설문 패키지를 제거합니다",
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="제외시키고자 하는 설문 패키지 id",
                type=openapi.TYPE_INTEGER,
            )
        ],
        responses={200: openapi.Response("deleted", WorkspaceSerializer)},
    )
    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance: WorkspaceComposition = self.get_object()
        workspace = get_object_or_404(Workspace, id=instance.workspace_id)
        instance.delete()

        workspace.refresh_from_db()
        serializer = self.get_serializer(workspace)

        return Response(serializer.data)

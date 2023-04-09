import datetime
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
from config.custom_pagination import CustomPagination
from config.exceptions import (
    InstanceNotFound,
    ConflictException,
    InvalidInputException,
    DuplicateInstance,
    UnprocessableException,
)
from config.paginator_inspector import CustomPaginationInspector
from config.permissions import IsOwnerOrReadOnly


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="요청을 보내는 유저의 모든 workspace 를 가져옵니다",
        pagination_class=CustomPagination,
        paginator_inspectors=[CustomPaginationInspector],
    ),
)
class WorkspaceListView(generics.ListCreateAPIView):
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
        responses={200: openapi.Response("ok", RoutineSerializer)},
    ),
)
class RoutineCreateView(generics.RetrieveAPIView, generics.CreateAPIView):
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
            required=["duration", "kick_off"],
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
                        required=["nth_day", "time"],
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
                            "external_resource": openapi.Schema(
                                type=openapi.TYPE_STRING, description="외부 리소스 (링크)"
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
        try:
            workspace = get_object_or_404(Workspace, id=kwargs.get("pk"))
        except Http404:
            raise InstanceNotFound("workspace with the provided id does not exist")

        try:
            existing_routine = self.get_object()
            if existing_routine:
                raise ConflictException(
                    "Routine for this workspace already exists. Workspace can only have one routine"
                )
        except Http404:
            pass

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
                workspace_id=workspace.id,
                kick_off_id=kick_off_package.id,
            )

        routine_service = RoutineService(routine_serializer.data.get("id"))

        # Create Routine Details
        routine_details = request.data.get("routines", None)
        if routine_details is not None:
            routine = routine_service.add_routine_details(routine_details)
            routine.refresh_from_db()
            return Response(
                self.get_serializer(routine).data, status=status.HTTP_201_CREATED
            )
        else:
            return Response(routine_serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(operation_summary="해당 id 의 루틴을 삭제합니다"),
)
@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="해당 id 의 루틴을 가져옵니다",
        responses={200: openapi.Response("ok", RoutineSerializer)},
    ),
)
class RoutineUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RoutineSerializer
    queryset = Routine.objects.all()
    allowed_methods = ["PATCH", "GET", "DELETE"]

    def get_queryset(self) -> QuerySet:
        return self.queryset.prefetch_related("routines").all()

    @swagger_auto_schema(
        operation_summary="해당 id 의 루틴을 수정합니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description="루틴의 duration 과 kickoff 서베이 패키지를 수정할 수 있습니다",
            properties={
                "duration": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="킥오프 서베이 이후부터의 루틴 날짜 수"
                ),
                "kick_off": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="kick off survey package 의 id",
                ),
            },
        ),
        responses={
            200: openapi.Response("ok", RoutineSerializer),
            404: "survey package with the provided id does not exist",
            409: "duration cannot be shorter than existing routine details' max nth_day value",
        },
    )
    def patch(self, request, *args, **kwargs):
        instance: Routine = self.get_object()
        routine_details_current_max = (
            instance.routines.order_by("-nth_day").first().nth_day
        )
        new_duration = request.data.get("duration", None)
        kick_off_id = request.data.get("kick_off", None)

        if new_duration is not None and new_duration < routine_details_current_max:
            raise ConflictException(
                "duration cannot be shorter than existing routine details' max nth_day value"
            )

        if kick_off_id is not None:
            try:
                survey_package = get_object_or_404(SurveyPackage, id=kick_off_id)
            except Http404:
                raise InstanceNotFound(
                    "survey package with the provided id does not exist"
                )

        serializer = self.get_serializer(instance, request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(updated_at=datetime.datetime.now())

        return Response(serializer.data)


@method_decorator(
    name="post",
    decorator=swagger_auto_schema(
        operation_summary="루틴에 세부 일정을 추가합니다",
        manual_parameters=[
            openapi.Parameter(
                "id", openapi.IN_PATH, type=openapi.TYPE_INTEGER, description="루틴의 id"
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["nth_day", "time"],
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
                "external_resource": openapi.Schema(
                    type=openapi.TYPE_STRING, description="외부 리소스 (링크)"
                ),
            },
        ),
        responses={
            201: openapi.Response("created", RoutineDetailSerializer),
            404: "'nth_day' cannot be larger than routine duration",
        },
    ),
)
class RoutineDetailCreateView(generics.CreateAPIView):
    serializer_class = RoutineDetailSerializer
    queryset = RoutineDetail.objects.all()

    def create(self, request, *args, **kwargs):
        routine_id = kwargs.get("pk")
        try:
            routine = get_object_or_404(Routine, id=routine_id)
        except Http404:
            raise InstanceNotFound("routine with the provided id does not exist")

        survey_package_id = request.data.get("survey_package", None)
        external_resource = request.data.get("external_resource", None)

        if not survey_package_id and not external_resource:
            raise InvalidInputException(
                "either survey package id or external resource should be provided for all routine details"
            )

        duration = routine.duration
        nth_day = request.data.get("nth_day", None)

        if nth_day is None:
            raise InvalidInputException("'nth_day' field is required")

        if nth_day > duration:
            raise InvalidInputException(
                "'nth_day' cannot be larger than routine duration"
            )

        try:
            existing_routine_detail = get_object_or_404(
                RoutineDetail,
                nth_day=request.data.get("nth_day", None),
                time=request.data.get("time", None),
                routine_id=routine_id,
            )
            if existing_routine_detail is not None:
                raise DuplicateInstance(
                    "routine detail with the same nth_day and time already exists"
                )

        except Http404:
            pass

        serializer = self.get_serializer(data=request.data)
        if survey_package_id is not None:
            if serializer.is_valid(raise_exception=True):
                serializer.save(
                    routine_id=routine_id,
                    survey_package_id=survey_package_id,
                )
        else:
            if serializer.is_valid(raise_exception=True):
                serializer.save(
                    routine_id=routine_id,
                )

        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
            raise InvalidInputException("'survey_packages' must be an array")

        service = WorkspaceService(workspace)
        workspace = service.add_survey_packages(survey_package_ids)

        serializer = self.get_serializer(workspace)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WorkspaceDestroySurveyPackageView(generics.DestroyAPIView):
    queryset = WorkspaceComposition.objects.all()
    serializer_class = WorkspaceSerializer

    def get_queryset(self):
        return self.queryset.filter(workspace_id=self.kwargs.get("pk"))

    def get_object(self):
        obj = _get_object_or_404(
            self.get_queryset(), survey_package_id=self.kwargs.get("survey_package_id")
        )
        self.check_object_permissions(self.request, obj)
        return obj

    @swagger_auto_schema(
        operation_summary="워크스페이스에서 설문 패키지를 제거합니다",
        operation_description="워크스페이스 루틴에 패키지가 걸려있다면, 삭제할 수 없습니다",
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_QUERY,
                description="워크스페이스 id",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "survey_package_id",
                openapi.IN_QUERY,
                description="제거하고자 하는 survey package의 id",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={200: openapi.Response("deleted", WorkspaceSerializer)},
    )
    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance: WorkspaceComposition = self.get_object()

        related_routine_details = RoutineDetail.objects.select_related(
            "routine"
        ).filter(
            routine__workspace_id=instance.workspace_id,
            survey_package_id=instance.survey_package_id,
        )

        if related_routine_details:
            raise UnprocessableException(
                "cannot exclude a survey package already linked to a routine"
            )

        workspace = get_object_or_404(Workspace, id=instance.workspace_id)
        instance.delete()

        workspace.refresh_from_db()
        serializer = self.get_serializer(workspace)

        return Response(serializer.data)

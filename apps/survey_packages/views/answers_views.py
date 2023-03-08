from typing import Any

from django.db.models import QuerySet, Prefetch
from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from apps.surveys.models import QuestionAnswer
from apps.surveys.serializers import QuestionAnswerSerializer
from apps.surveys.services import QuestionAnswerService
from apps.workspaces.models import (
    Workspace,
    WorkspaceComposition,
    RoutineDetail,
)
from apps.workspaces.serializers import WorkspaceCompositionSerializer
from config.exceptions import InstanceNotFound
from config.permissions import AdminOnly


class SurveyPackageAnswerCreateView(generics.CreateAPIView):
    queryset = QuestionAnswer.objects.all()
    serializer_class = QuestionAnswerSerializer

    @swagger_auto_schema(
        tags=["survey-answer"],
        operation_summary="해당 survey package 에 대한 피험자의 응답을 생성합니다",
        operation_description="헤더의 Authorization 를 이용하여 앱 이용자임을 식별합니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "key": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="워크스페이스 uuid + 피험자 고유 번호 (앱에 저장해둬야 합니다)",
                ),
                "answers": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "question_id": openapi.Schema(
                                type=openapi.TYPE_INTEGER, description="question id"
                            ),
                            "answer": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="문항 응답을 순서대로 적습니다. 구분자는 $입니다.",
                            ),
                        },
                    ),
                ),
            },
        ),
        responses={
            201: openapi.Response("created", QuestionAnswerSerializer(many=True))
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        key = request.data.get("key")
        if key is None:
            raise ValidationError("key is required")

        workspace_uuid = key[:22]
        respondent_id = key[22:]

        try:
            workspace = get_object_or_404(Workspace, uuid=workspace_uuid)
        except Http404:
            raise InstanceNotFound("no workspace by the provided key")

        service = QuestionAnswerService(
            workspace.id, kwargs.get("pk"), request.user, respondent_id
        )

        answers = service.create_answers(request.data)
        service.record_respondent()

        serializer = self.get_serializer(answers, many=True)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SurveyPackageAnswerDownloadView(generics.RetrieveAPIView):
    permission_classes = [AdminOnly]
    serializer_class = WorkspaceCompositionSerializer
    queryset = WorkspaceComposition.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["workspace_id"]

    def get_queryset(self) -> QuerySet:
        survey_package_id = self.kwargs.get("pk")
        workspace_id = self.request.GET.get("workspace_id")
        print(survey_package_id, workspace_id)

        try:
            workspace_composition = get_object_or_404(
                WorkspaceComposition,
                survey_package_id=survey_package_id,
                workspace_id=workspace_id,
            )
        except Http404:
            raise InstanceNotFound(
                "survey package does not exist in the provided workspace"
            )
        return self.queryset.filter(
            survey_package_id=survey_package_id, workspace_id=workspace_id
        ).select_related("survey_package", "workspace")

    @swagger_auto_schema(
        operation_summary="survey package 의 응답을 엑셀 파일 형태로 다운로드 합니다",
        tags=["survey-answer"],
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_PATH,
                description="survey package id",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "workspaceId",
                openapi.IN_QUERY,
                description="다운로드하고자 하는 survey package 가 속해있는 workspace id",
                type=openapi.TYPE_INTEGER,
            ),
        ],
    )
    def get(self, request, *args, **kwargs) -> Response:
        instance: WorkspaceComposition = self.get_object()

        routine_id = instance.workspace.routine.id
        routine_detail: RoutineDetail = RoutineDetail.objects.filter(
            routine_id=routine_id, survey_package_id=instance.id
        ).first()

        workspace_name: str = instance.workspace.name
        package_name = instance.survey_package.title
        nth_day = routine_detail.nth_day
        time = routine_detail.time

        return Response(status=status.HTTP_204_NO_CONTENT)

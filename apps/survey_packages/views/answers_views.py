from datetime import datetime
from tempfile import NamedTemporaryFile
from typing import Any

from django.db.models import QuerySet
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.survey_packages.services import ResponseExportService
from apps.surveys.models import QuestionAnswer
from apps.surveys.serializers import QuestionAnswerSerializer
from apps.surveys.services import QuestionAnswerService
from apps.workspaces.models import (
    Workspace,
    WorkspaceComposition,
    RoutineDetail,
    Routine,
)
from apps.workspaces.serializers import (
    WorkspaceCompositionSerializer,
    RoutineSerializer,
)
from config.exceptions import InstanceNotFound, InvalidInputException
from config.permissions import AdminOnly


class SurveyPackageAnswerCreateView(generics.CreateAPIView):
    queryset = QuestionAnswer.objects.all()
    serializer_class = QuestionAnswerSerializer

    @swagger_auto_schema(
        tags=["survey-answer"],
        operation_summary="해당 survey package 에 대한 피험자의 응답을 생성합니다",
        operation_description="헤더의 Authorization 를 이용하여 앱 이용자임을 식별합니다",
        manual_parameters=[
            openapi.Parameter(
                "routine",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="루틴 정보를 함께 받을 것인지 표기합니다. 루틴 정보를 함께 받으려면 ?routine=y 의 형태로 query string 을 포함시켜주세요. 받지 않으려면 query string 을 제외합니다",
            )
        ],
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
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "answers": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        description="생성한 응답들",
                        items=openapi.Schema(type=openapi.TYPE_OBJECT),
                    ),
                    "routine": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description="/workspace/{id}/routines 와 동일",
                    ),
                },
            )
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        key = request.data.get("key")
        if key is None:
            raise InvalidInputException("key is required")

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

        routine_data = None
        if request.GET.get("routine"):
            try:
                routine = get_object_or_404(Routine, workspace_id=workspace.id)
                routine_data = RoutineSerializer(routine).data
            except Http404:
                pass

        return Response(
            {"answers": serializer.data, "routine": routine_data},
            status=status.HTTP_201_CREATED,
        )


class SurveyPackageAnswerDownloadView(APIView):
    permission_classes = [AdminOnly]

    def get_object(self, pk):
        survey_package_id = pk
        workspace_query: str = self.request.GET.get("workspace", None)

        if workspace_query is None:
            raise InvalidInputException("workspace id not set in query string")

        if not workspace_query.isnumeric():
            raise InvalidInputException("workspace must be in number format")

        workspace_id = int(workspace_query)

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
        queryset = WorkspaceComposition.objects.filter(
            survey_package_id=survey_package_id, workspace_id=workspace_id
        ).select_related("survey_package", "workspace")

        return queryset.first()

    @swagger_auto_schema(
        operation_summary="survey package 의 응답을 엑셀 파일 형태로 다운로드 합니다",
        tags=["survey-answer"],
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_PATH,
                description="survey package id",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                "workspace",
                openapi.IN_QUERY,
                description="다운로드하고자 하는 survey package 가 속해있는 workspace id",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
    )
    def get(self, request, pk, format=None) -> HttpResponse:
        instance: WorkspaceComposition = self.get_object(pk)

        service = ResponseExportService(
            instance.workspace,
            instance.survey_package,
        )

        package_name = instance.survey_package.title
        package_name = package_name.replace(" ", "_")

        wb = service.export_to_worksheet()

        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            tmp.seek(0)
            stream = tmp.read()

        response = HttpResponse(
            content=stream,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            status=204,
        )
        response.headers[
            "Content-Disposition"
        ] = f'attachment; filename={package_name}-{datetime.now().strftime("%Y%m%d%H%M")}.xlsx'

        return response

from typing import Any

from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from apps.surveys.models import QuestionAnswer
from apps.surveys.serializers import QuestionAnswerSerializer
from apps.surveys.services import QuestionAnswerService
from apps.workspaces.models import Workspace
from config.exceptions import InstanceNotFound


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

        serializer = self.get_serializer(answers, many=True)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

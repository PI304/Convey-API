from typing import Any, List

from django.db.models import QuerySet, Prefetch
from datetime import datetime
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response

from apps.surveys.models import SurveySector, Survey, SectorQuestion
from apps.surveys.serializers import (
    SimpleSurveySerializer,
    SurveySerializer,
    SurveySectorSerializer,
)
from apps.surveys.services import SurveyService
from config.permissions import AdminOnly, IsAdminOrReadOnly, IsAuthorOrReadOnly


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="요청을 보내는 유저가 만든 모든 survey 를 가져옵니다",
        responses={200: SimpleSurveySerializer(many=True)},
    ),
)
class SurveyListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, AdminOnly]
    queryset = Survey.objects.all()
    serializer_class = SimpleSurveySerializer

    def get_queryset(self) -> QuerySet:
        return self.queryset.filter(author_id=self.request.user.id).all()

    @swagger_auto_schema(
        operation_summary="기본 정보를 입력 받아 빈 survey 를 만듭니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING, description="설문 제목"),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING, description="설문 설명"
                ),
                "abbr": openapi.Schema(
                    type=openapi.TYPE_STRING, description="abbreviation"
                ),
            },
        ),
        responses={201: openapi.Response("created", SimpleSurveySerializer)},
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author_id=request.user.id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="survey의 기본 정보와 하위 sector 들을 모두 가져옵니다",
        responses={200: openapi.Response("ok", SurveySerializer)},
    ),
)
@method_decorator(
    name="patch",
    decorator=swagger_auto_schema(
        operation_summary="설문의 기본 정보를 수정합니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING, description="설문 제목"),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING, description="설문 설명"
                ),
                "abbr": openapi.Schema(
                    type=openapi.TYPE_STRING, description="abbreviation"
                ),
            },
        ),
        responses={200: openapi.Response("updated", SimpleSurveySerializer)},
    ),
)
@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        operation_summary="설문을 완전히 삭제합니다. 관련된 모든 데이터들이 삭제됩니다",
        responses={204: "no content"},
    ),
)
class SurveyDetailView(generics.RetrieveUpdateDestroyAPIView):
    allowed_methods = ["PUT", "GET", "DELETE", "PATCH"]
    queryset = Survey.objects.all()
    serializer_class = SurveySerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminOrReadOnly,
        IsAuthorOrReadOnly,
    ]

    def get_queryset(self) -> QuerySet:
        return self.queryset.prefetch_related(
            Prefetch(
                "sectors",
                queryset=SurveySector.objects.prefetch_related(
                    "common_choices",
                    Prefetch(
                        "questions",
                        queryset=SectorQuestion.objects.prefetch_related("choices"),
                    ),
                ),
            )
        )

    @swagger_auto_schema(
        operation_summary="설문의 내용을 구성합니다. 기본 정보를 제외한 기존의 설문 내용은 삭제되고 새로 생성됩니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            description="sector 로 구성된 list",
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "title": openapi.Schema(
                        type=openapi.TYPE_STRING, description="sector 제목"
                    ),
                    "description": openapi.Schema(
                        type=openapi.TYPE_STRING, description="sector 에 더해질 설명"
                    ),
                    "question_type": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description=f"가능한 타입은 {str(SurveySector.QuestionType.values)}",
                    ),
                    "common_choices": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        description="하나의 섹터에 공통 선지가 적용되는 경우 ex) 리커트",
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "number": openapi.Schema(
                                    type=openapi.TYPE_INTEGER,
                                    description="문제 문항 번호",
                                ),
                                "content": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="실제 선지 내용",
                                ),
                                "is_descriptive": openapi.Schema(
                                    type=openapi.TYPE_BOOLEAN,
                                    description="서술단답 여부",
                                ),
                                "desc_form": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="문자열 치환자는 '%s' 숫자 치환자는 '%d'",
                                ),
                            },
                        ),
                    ),
                    "questions": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        description="실제 문항 list",
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "number": openapi.Schema(
                                    type=openapi.TYPE_INTEGER, description="문항 번호"
                                ),
                                "content": openapi.Schema(
                                    type=openapi.TYPE_STRING, description="실제 문항 내용"
                                ),
                                "is_required": openapi.Schema(
                                    type=openapi.TYPE_BOOLEAN,
                                    default=True,
                                    description="필수 문항 여부",
                                ),
                                "linked_sector": openapi.Schema(
                                    type=openapi.TYPE_INTEGER, description="연결 섹터의 id"
                                ),
                                "choices": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    description="문제와 연결될 선지구성",
                                    items=openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        description="위 공통 선지와 동일",
                                    ),
                                ),
                            },
                        ),
                    ),
                },
            ),
        ),
        responses={200: openapi.Response("ok", SurveySerializer)},
    )
    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        survey = self.get_object()

        service = SurveyService(survey)
        service.delete_related_sectors()

        sectors = service.create_sectors(request.data)

        survey.refresh_from_db()

        serializer = self.get_serializer(survey)

        return Response(serializer.data)

    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        serializer = SimpleSurveySerializer(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save(updated_at=datetime.now())
        return Response(serializer.data)


# TODO: 연결 문항 따로 관리

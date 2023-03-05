from datetime import datetime
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

from apps.survey_packages.models import (
    PackageSubjectSurvey,
    PackageSubject,
    PackagePart,
)
from apps.survey_packages.serializers import (
    PackageSubjectSerializer,
    PackageSubjectSurveySerializer,
)
from apps.survey_packages.services import SurveyPackageService
from config.exceptions import InstanceNotFound


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="part 하위의 모든 subject 를 가져옵니다",
        manual_parameters=[
            openapi.Parameter(
                "id", openapi.IN_PATH, description="part id", type=openapi.TYPE_INTEGER
            )
        ],
        # responses={200: openapi.Response("ok", PackageSubjectSerializer(many=True))},
    ),
)
class PackageSubjectListView(generics.ListCreateAPIView):
    serializer_class = PackageSubjectSerializer
    queryset = PackageSubject.objects.all()

    def get_queryset(self) -> QuerySet:
        return self.queryset.filter(package_part_id=self.kwargs.get("pk"))

    @swagger_auto_schema(
        operation_summary="설문 패키지의, 대주제 (디바이더) 하위의 소주제를 추가합니다",
        manual_parameters=[
            openapi.Parameter(
                "id", openapi.IN_PATH, description="part id", type=openapi.TYPE_INTEGER
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "number": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="문항 번호",
                ),
                "title": openapi.Schema(type=openapi.TYPE_STRING, description="소주제 제목"),
            },
        ),
        responses={
            201: openapi.Response("created", PackageSubjectSerializer),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            part = get_object_or_404(PackagePart, id=kwargs.get("pk"))
        except Http404:
            raise InstanceNotFound("part not found")

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(package_part_id=part.id)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        operation_summary="part 하위의 subject 를 삭제합니다. 이때 subject 내 포함되어 있던 survey 구성도 삭제됩니다",
        responses={204: "no content"},
    ),
)
@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="id에 따라 subject 를 가져옵니다",
        responses={200: openapi.Response("ok", PackageSubjectSerializer)},
    ),
)
class PackageSubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PackageSubjectSerializer
    queryset = PackageSubject.objects.all()
    allowed_methods = ["GET", "PATCH", "DELETE", "PUT"]

    @swagger_auto_schema(
        operation_summary="subject 의 제목과 번호를 수정합니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "number": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="문항 번호",
                ),
                "title": openapi.Schema(
                    type=openapi.TYPE_STRING, description="part 제목"
                ),
            },
        ),
    )
    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save(updated_at=datetime.now())

        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="설문 패키지의, 대주제 (디바이더) 의, 소주제에 포함될 설문을 구성합니다",
        operation_description="기존의 구성이 있다면 덮어씁니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "title": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="설문 제목, 설문 생성 시 지정했던 제목을 사용해도 되며, null 로 설정 시 별도의 설문 제목을 포함하지 않습니다",
                    ),
                    "survey": openapi.Schema(
                        type=openapi.TYPE_INTEGER, description="survey id"
                    ),
                },
            ),
        ),
        responses={
            200: openapi.Response("created", PackageSubjectSerializer),
        },
    )
    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        SurveyPackageService.delete_related_surveys(instance.id)

        SurveyPackageService.associate_subject_with_surveys(instance.id, request.data)

        instance.refresh_from_db()
        serializer = self.get_serializer(instance)

        return Response(serializer.data)

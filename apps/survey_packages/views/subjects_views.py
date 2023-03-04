from typing import Any

from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.request import Request
from rest_framework.response import Response

from apps.survey_packages.models import PackageSubjectSurvey, PackageSubject
from apps.survey_packages.serializers import (
    PackageSubjectSerializer,
    PackageSubjectSurveySerializer,
)
from apps.survey_packages.services import SurveyPackageService
from config.exceptions import InstanceNotFound


class PackageSubjectCreateView(generics.CreateAPIView):
    serializer_class = PackageSubjectSurveySerializer
    queryset = PackageSubjectSurvey.objects.all()

    @swagger_auto_schema(
        operation_summary="설문 패키지의, 대주제 (디바이더) 의, 소주제에 포함될 설문을 구성합니다",
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
            201: openapi.Response("created", PackageSubjectSerializer),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # try:
        #     subject = get_object_or_404(PackageSubject, id=kwargs.get("pk"))
        # except Http404:
        #     raise InstanceNotFound("subject not found")
        #
        # service = SurveyPackageService(package)
        #
        # part = service.create_part(request.data, package.id)
        #
        # part.refresh_from_db()
        # serializer = self.get_serializer(part)
        #
        # return Response(serializer.data)
        pass


class PackageSubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    pass

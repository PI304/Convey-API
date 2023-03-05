from datetime import datetime
from typing import Any

from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response

from apps.survey_packages.models import PackagePart, SurveyPackage
from apps.survey_packages.serializers import PackagePartSerializer
from apps.survey_packages.services import SurveyPackageService
from config.exceptions import InstanceNotFound


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="설문 패키지 하위의 모든 parts 를 가져옵니다",
        responses={200: openapi.Response("ok", PackagePartSerializer(many=True))},
    ),
)
class PackagePartListView(generics.ListCreateAPIView):
    serializer_class = PackagePartSerializer
    queryset = PackagePart.objects.all()

    @swagger_auto_schema(
        operation_summary="설문 패키지 하위에 하나의 대주제 (디바이더) 를 생성합니다",
        operation_description="대주제 하위의 소주제까지 함께 구성합니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="디바이더 제목",
                ),
                "subjects": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "number": openapi.Schema(
                                type=openapi.TYPE_INTEGER,
                                description="문항 번호",
                            ),
                            "title": openapi.Schema(
                                type=openapi.TYPE_STRING, description="소주제 제목"
                            ),
                        },
                    ),
                ),
            },
        ),
        responses={
            201: openapi.Response("created", PackagePartSerializer),
        },
    )
    def post(self, request, *args, **kwargs) -> Response:
        try:
            package = get_object_or_404(SurveyPackage, id=kwargs.get("pk"))
        except Http404:
            raise InstanceNotFound("package not found")

        service = SurveyPackageService(package)

        part = service.create_part(request.data, package.id)

        part.refresh_from_db()
        serializer = self.get_serializer(part)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        operation_summary="part 를 삭제합니다. survey 원본을 제외한, part 구성과 관련된 하위 데이터들을 모두 삭제됩니다",
        responses={204: "no content"},
    ),
)
@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="id에 따라 part 를 가져옵니다",
        responses={200: openapi.Response("ok", PackagePartSerializer)},
    ),
)
class PackagePartDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PackagePartSerializer
    queryset = PackagePart.objects.all()
    allowed_methods = ["GET", "DELETE", "PATCH"]

    @swagger_auto_schema(
        operation_summary="part 의 제목을 수정합니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING, description="part 제목")
            },
        ),
    )
    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(updated_at=datetime.now())

        return Response(serializer.data)

from django.http import Http404
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.response import Response

from apps.survey_packages.models import PackagePart, SurveyPackage
from apps.survey_packages.serializers import PackagePartSerializer
from apps.survey_packages.services import SurveyPackageService
from config.exceptions import InstanceNotFound


class PackagePartCreateView(generics.CreateAPIView):
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

        return Response(serializer.data)


class PackagePartDetailView(generics.RetrieveUpdateDestroyAPIView):
    pass

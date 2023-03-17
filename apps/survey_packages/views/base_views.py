from tempfile import NamedTemporaryFile
from typing import Any

from django.db.models import QuerySet, Prefetch
from django.http import Http404, HttpResponse
from datetime import datetime

from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, permissions
from rest_framework.generics import get_object_or_404 as _get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.survey_packages.models import (
    SurveyPackage,
    PackageContact,
    PackagePart,
    PackageSubject,
    PackageSubjectSurvey,
)
from apps.survey_packages.serializers import (
    SurveyPackageSerializer,
    SimpleSurveyPackageSerializer,
)
from apps.survey_packages.services import (
    SurveyPackageService,
    SurveyPackageExportService,
)
from apps.surveys.models import SectorQuestion, Survey, SurveySector
from apps.workspaces.models import Routine, Workspace
from config.exceptions import (
    InstanceNotFound,
    UnprocessableException,
    InvalidInputException,
)
from config.permissions import AdminOnly, IsAuthorOrReadOnly


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="요청을 보내는 유저가 만든 모든 survey package 를 가져옵니다",
    ),
)
class SurveyPackageListView(generics.ListCreateAPIView):
    serializer_class = SimpleSurveyPackageSerializer
    queryset = SurveyPackage.objects.all()
    permission_classes = [permissions.IsAuthenticated, AdminOnly]

    def get_queryset(self) -> QuerySet:
        return (
            self.queryset.filter(author_id=self.request.user.id)
            .select_related("author")
            .prefetch_related("contacts")
        )

    @swagger_auto_schema(
        operation_summary="기본 정보만이 채워진 빈 설문 패키지를 만듭니다",
        operation_description="logo 첨부 시, multipart/form-data 로 전송합니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["title", "description", "access_code", "manager", "contacts"],
            properties={
                "title": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="설문 패키지 이름",
                ),
                "logo": openapi.Schema(type=openapi.TYPE_FILE, description="로고 파일"),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING, description="패키지 설명"
                ),
                "access_code": openapi.Schema(
                    type=openapi.TYPE_STRING, description="피험자가 설문 패키지에 접근할 때 필요한 코드"
                ),
                "manager": openapi.Schema(
                    type=openapi.TYPE_STRING, description="담당자 이름"
                ),
                "contacts": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "type": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="'email' or 'phone'",
                            ),
                            "content": openapi.Schema(
                                type=openapi.TYPE_STRING, description="연락처 정보"
                            ),
                        },
                    ),
                ),
            },
        ),
        responses={
            201: openapi.Response("created", SimpleSurveyPackageSerializer),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if "contacts" in request.data and type(request.data["contacts"]) != list:
            raise InvalidInputException("'contacts' field must be a list")

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(author_id=request.user.id)

        service = SurveyPackageService(serializer.data.get("id"))

        contacts = request.data.get("contacts", None)
        print("contacts type", contacts)
        if contacts:
            package = service.add_contacts(contacts)
            return Response(
                self.get_serializer(package).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(
    name="delete",
    decorator=swagger_auto_schema(
        operation_summary="설문 패키지를 완전히 삭제합니다. 독립적으로 존재하는 survey 를 제외하고 관련된 모든 데이터들이 삭제됩니다",
        responses={
            204: "No content",
        },
    ),
)
@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="설문 패키지의 정보를 전부 가져옵니다",
        responses={200: openapi.Response("ok", SurveyPackageSerializer)},
    ),
)
class SurveyPackageDetailView(generics.RetrieveUpdateDestroyAPIView):
    allowed_methods = ["DELETE", "GET", "PATCH"]
    queryset = SurveyPackage.objects.all()
    serializer_class = SurveyPackageSerializer
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self) -> QuerySet:
        return self.queryset.select_related("author").prefetch_related(
            "contacts",
            Prefetch(
                "parts",
                queryset=PackagePart.objects.prefetch_related(
                    Prefetch(
                        "subjects",
                        queryset=PackageSubject.objects.prefetch_related(
                            Prefetch(
                                "surveys",
                                queryset=PackageSubjectSurvey.objects.select_related(
                                    "survey"
                                ).prefetch_related(
                                    Prefetch(
                                        "survey__sectors",
                                        queryset=SurveySector.objects.prefetch_related(
                                            "common_choices",
                                            Prefetch(
                                                "questions",
                                                queryset=SectorQuestion.objects.prefetch_related(
                                                    "choices"
                                                ),
                                            ),
                                        ),
                                    )
                                ),
                            )
                        ),
                    )
                ),
            ),
        )

    @swagger_auto_schema(
        operation_summary="설문 패키지 기본 정보를 수정합니다",
        operation_description="연락처 정보를 수정하는 경우, 수정된 데이터로 교체됩니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "title": openapi.Schema(
                    type=openapi.TYPE_STRING, description="설문 패키지의 제목"
                ),
                "logo": openapi.Schema(type=openapi.TYPE_FILE, description="로고 파일"),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING, description="설문 패키지 설명"
                ),
                "manager": openapi.Schema(
                    type=openapi.TYPE_STRING, description="설문 패키지 담당자"
                ),
                "contacts": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "type": openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="연락처 정보의 타입, email / phone",
                            ),
                            "content": openapi.Schema(
                                type=openapi.TYPE_STRING, description="연락처 정보"
                            ),
                        },
                    ),
                ),
            },
        ),
        responses={200: openapi.Response("updated", SimpleSurveyPackageSerializer)},
    )
    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if "contacts" in request.data and type(request.data["contacts"]) != list:
            raise InvalidInputException("'contacts' field must be a list")

        instance = self.get_object()
        serializer = SimpleSurveyPackageSerializer(
            instance, data=request.data, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            instance = serializer.save(updated_at=datetime.now())

        if "contacts" in request.data:
            try:
                PackageContact.objects.filter(survey_package_id=instance.id).delete()
            except:
                pass

            service = SurveyPackageService(instance)

            contacts = request.data.get("contacts")
            print(contacts, type(contacts))
            service.add_contacts(request.data.get("contacts", None))

        return Response(
            SimpleSurveyPackageSerializer(instance).data, status=status.HTTP_200_OK
        )


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="워크스페이스와 피험자에 대응하는 kick-off survey 를 가져옵니다",
        manual_parameters=[
            openapi.Parameter(
                "key",
                openapi.IN_QUERY,
                description="워크스페이스 고유 uuid + 피험자 고유번호",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                "code",
                openapi.IN_QUERY,
                description="워크스페이스에 접근하기 위한 비밀번호",
                type=openapi.TYPE_STRING,
                required=True,
            ),
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "workspace": openapi.Schema(
                        type=openapi.TYPE_INTEGER, description="워크스페이스 id"
                    ),
                    "survey_package": openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description="/survey-packages/{id}/ 응답과 동일",
                    ),
                },
            )
        },
    ),
)
class KickOffSurveyView(generics.RetrieveAPIView):
    serializer_class = SurveyPackageSerializer
    queryset = SurveyPackage.objects.all()

    def get_routine(self) -> Routine:
        key = self.request.GET.get("key", None)
        code = self.request.GET.get("code", None)

        if not (key and code):
            raise InvalidInputException("'key' and 'code'should be set in query string")

        uuid = key[:22]
        subject_id = key[22:]

        try:
            workspace = (
                Workspace.objects.filter(uuid=uuid).select_related("routine").first()
            )
            if workspace.access_code != code:
                raise UnprocessableException("access code does not match")
        except Http404:
            raise InstanceNotFound("no workspace by the provided key")

        return workspace.routine

    def get_queryset(self) -> QuerySet:
        return self.queryset.select_related("author").prefetch_related(
            "contacts",
            Prefetch(
                "parts",
                queryset=PackagePart.objects.prefetch_related(
                    Prefetch(
                        "subjects",
                        queryset=PackageSubject.objects.prefetch_related(
                            Prefetch(
                                "surveys",
                                queryset=PackageSubjectSurvey.objects.select_related(
                                    "survey"
                                ).prefetch_related(
                                    Prefetch(
                                        "survey__sectors",
                                        queryset=SurveySector.objects.prefetch_related(
                                            "common_choices",
                                            Prefetch(
                                                "questions",
                                                queryset=SectorQuestion.objects.prefetch_related(
                                                    "choices"
                                                ),
                                            ),
                                        ),
                                    )
                                ),
                            )
                        ),
                    )
                ),
            ),
        )

    def get_object(self) -> SurveyPackage:
        associated_routine = self.get_routine()
        return _get_object_or_404(
            self.get_queryset(), id=associated_routine.kick_off_id
        )


class SurveyPackageDownloadView(APIView):
    serializer_class = SurveyPackageSerializer
    queryset = SurveyPackage.objects.all()

    @swagger_auto_schema(
        operation_summary="survey package 의 문항 구성을 엑셀 형태로 다운로드 합니다",
        manual_parameters=[
            openapi.Parameter(
                "id",
                openapi.IN_PATH,
                description="survey package id",
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
        ],
        responses={204: "download success"},
    )
    def get(self, request, pk, format=None) -> HttpResponse:
        try:
            survey_package = get_object_or_404(SurveyPackage, id=pk)
        except Http404:
            raise InstanceNotFound("survey package for the provided id does not exist")

        service = SurveyPackageExportService(survey_package.id)

        package_name = survey_package.title
        package_name = package_name.replace(" ", "_")

        wb = service.export_to_workbook()

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

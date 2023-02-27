from typing import Any

from django.db.models import QuerySet, Prefetch
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, permissions, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.survey_packages.models import (
    SurveyPackage,
    PackagePart,
    PackageSubject,
    PackageSubjectSurvey,
)
from apps.survey_packages.serializers import (
    SurveyPackageSerializer,
    PackagePartSerializer,
    SimpleSurveyPackageSerializer,
)
from apps.survey_packages.services import SurveyPackageService
from apps.users.services import UserService
from apps.workspaces.models import Routine, Workspace
from config.exceptions import InstanceNotFound, UnprocessableException
from config.permissions import AdminOnly


@method_decorator(
    name="get",
    decorator=swagger_auto_schema(
        operation_summary="요청을 보내는 유저가 만든 모든 survey package 를 가져옵니다",
    ),
)
class SurveyPackageListView(generics.ListCreateAPIView):
    serializer_class = SurveyPackageSerializer
    queryset = SurveyPackage.objects.all()
    permission_classes = [permissions.IsAuthenticated, AdminOnly]

    def get_queryset(self) -> QuerySet:
        return self.queryset.filter(author_id=self.request.user.id)

    @swagger_auto_schema(
        operation_summary="기본 정보만이 채워진 빈 설문 패키지를 만듭니다",
        operation_description="multipart/form-data 로 전송합니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
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
            201: openapi.Response("created", SurveyPackageSerializer),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exceptions=True):
            serializer.save(author_id=request.user.id)

        service = SurveyPackageService(serializer.data.get("id"))

        contacts = request.data.get("contacts", None)
        if contacts:
            package = service.add_contacts(contacts)
            return Response(
                self.get_serializer(package).data, status=status.HTTP_201_CREATED
            )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(
    name="destroy",
    decorator=swagger_auto_schema(
        operation_summary="설문 패키지를 완전히 삭제합니다. 관련된 모든 데이터들이 삭제됩니다",
        responses={
            204: "No content",
        },
    ),
)
class SurveyPackageDetailView(
    generics.UpdateAPIView, mixins.DestroyModelMixin, generics.ListAPIView
):
    allowed_methods = ["PUT", "DELETE", "GET", "PATCH"]
    queryset = SurveyPackage.objects.all()
    serializer_class = SurveyPackageSerializer

    @swagger_auto_schema(
        operation_summary="하나의 패키지 안에 있는 모든 Parts 를 가져옵니다",
        responses={
            400: "No cookies attached",
            409: "Verification code does not match",
        },
    )
    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        queryset = PackagePart.objects.filter(
            survey_package_id=kwargs.get("pk")
        ).prefetch_related(
            Prefetch(
                "subjects",
                queryset=PackageSubject.objects.prefetch_related(
                    Prefetch(
                        "surveys",
                        queryset=PackageSubjectSurvey.objects.prefetch_related(
                            Prefetch("survey_content")
                        ),
                    ),
                ),
            )
        )
        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PackagePartSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="빈 설문 패키지를 구성합니다. 기존의 설문 패키지가 있는 경우는 해당되지 않습니다",
        operation_description="설문 패키지 하위에는 Parts -> Subjects -> Surveys 가 존재합니다. 설문 패키지를 생성할 때에는 Parts 를 하나의 요소로 하여 리스트를 전달합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "title": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="PART (디바이더) 의 이름",
                    ),
                    "subjects": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        description="디바이더 (PART) 아래 주제",
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "title": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="디바이더 아래의 주제 이름",
                                ),
                                "surveys": openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    description="연결할 survey ID들",
                                    items=openapi.Schema(
                                        type=openapi.TYPE_INTEGER,
                                        description="survey id",
                                    ),
                                ),
                            },
                        ),
                    ),
                },
            ),
        ),
        responses={
            400: "No cookies attached",
            409: "Verification code does not match",
        },
    )
    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # TODO: survey 구현 후 작업
        pass

    @swagger_auto_schema(
        operation_summary="설문 패키지 기본 정보를 수정합니다",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["title", "logo", "description", "manager", "contacts"],
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
        instance = self.get_object()
        serializer = SimpleSurveyPackageSerializer(
            instance, data=request.data, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save(updated_at=timezone.now())

        return Response(serializer.data, status=status.HTTP_200_OK)


class KickOffSurveyView(APIView):
    def get_routine(self) -> Routine:
        key = self.request.GET.get("uuid", None)
        code = self.request.GET.get("code", None)

        if not (key and code):
            raise ValidationError("'key' and 'code'should be set in query string")

        uuid = key[:22]
        subject_id = key[22:]

        try:
            workspace = (
                Workspace.objects.filter(uuid=uuid).select_related("routine").first()
            )
            if workspace.access_code != code:
                raise UnprocessableException("access code does not match")
        except Http404:
            raise InstanceNotFound("no workspace by the provided uuid")

        return workspace.routine

    @swagger_auto_schema(
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
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> HttpResponseRedirect:
        associated_routine = self.get_routine()

        return HttpResponseRedirect(
            redirect_to=f"/api/survey-packages/{associated_routine.kick_off_id}/"
        )

from typing import List

from django.urls import path, URLResolver, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

api_info = openapi.Info(
    title="Convey - API Doc",
    default_version="v1",
    description="Convey Application을 위한 API 문서\n**camel case 호환가능",
    terms_of_service="https://www.google.com/policies/terms/",
    contact=openapi.Contact(email="earthlyz9.dev@gmail.com"),
)

SchemaView = get_schema_view(
    api_info,
    public=True,
    permission_classes=([permissions.AllowAny]),
    validators=["flex"],
    urlconf="config.urls_v1",
)


@api_view(["GET"])
def hello_world(request: Request) -> Response:
    return Response("Go to '/api/swagger' or '/api/redoc' for api documentation")


urlpatterns: List[URLResolver] = [
    path("", hello_world),
    path("auth", include("apps.users.auth_urls")),
    # path("users/", include("apps.users.urls")),
    path("workspaces", include("apps.workspaces.urls")),
    path("surveys", include("apps.surveys.urls")),
    path("survey-packages", include("apps.survey_packages.urls")),
]

urlpatterns += [
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)/?$",
        SchemaView.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/?$",
        SchemaView.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/?$",
        SchemaView.with_ui("redoc", cache_timeout=0),
        name="schema-redoc-ui",
    ),
]

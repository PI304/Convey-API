from django.urls import path, URLPattern

from apps.survey_packages.views import (
    base_views,
    answers_views,
    parts_views,
    subjects_views,
)


urlpatterns: list[URLPattern] = [
    path("", base_views.SurveyPackageListView.as_view(), name="survey_packages_list"),
    path(
        "/<int:pk>",
        base_views.SurveyPackageDetailView.as_view(),
        name="survey_packages_details",
    ),
    path(
        "/<int:pk>/answers",
        answers_views.SurveyPackageAnswerCreateView.as_view(),
        name="survey_package_answers_list",
    ),
    path("/kick-off", base_views.KickOffSurveyView.as_view(), name="kickoff_survey"),
    path(
        "/<int:pk>/parts",
        parts_views.PackagePartListView.as_view(),
        name="package_part_create",
    ),
    path(
        "/parts/<int:pk>",
        parts_views.PackagePartDetailView.as_view(),
        name="package_part_create",
    ),
    path(
        "/parts/<int:pk>/subjects",
        subjects_views.PackageSubjectListView.as_view(),
        name="package_part_create",
    ),
    path(
        "/parts/subjects/<int:pk>",
        subjects_views.PackageSubjectDetailView.as_view(),
        name="package_part_create",
    ),
]

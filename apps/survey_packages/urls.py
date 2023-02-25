from django.urls import path, URLPattern

from apps.survey_packages.views.base_views import (
    SurveyPackageListView,
    SurveyPackageDetailView,
)

from apps.survey_packages.views.answers_views import (
    SurveyPackageAnswerListView,
    SurveyPackageAnswerDetailView,
)

urlpatterns: list[URLPattern] = [
    path("", SurveyPackageListView.as_view(), name="survey_packages_list"),
    path(
        "<int:pk>/",
        SurveyPackageDetailView.as_view(),
        name="survey_packages_details",
    ),
    path(
        "<int:pk>/answers/",
        SurveyPackageAnswerListView.as_view(),
        name="survey_package_answers_list",
    ),
]

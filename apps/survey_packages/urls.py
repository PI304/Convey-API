from django.urls import path, URLPattern

from apps.survey_packages.views.base_views import (
    SurveyPackageListView,
    SurveyPackageDetailView,
    KickOffSurveyView,
)

from apps.survey_packages.views.answers_views import (
    SurveyPackageAnswerCreateView,
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
        SurveyPackageAnswerCreateView.as_view(),
        name="survey_package_answers_list",
    ),
    path("kick-off/", KickOffSurveyView.as_view(), name="kickoff_survey"),
]

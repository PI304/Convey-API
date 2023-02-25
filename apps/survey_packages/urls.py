from django.urls import path

from apps.survey_packages.views import SurveyPackageListView, SurveyPackageDetailView

urlpatterns = [
    path("", SurveyPackageListView.as_view(), name="survey_packages_list"),
    path(
        "<int:pk>/",
        SurveyPackageDetailView.as_view(),
        name="survey_packages_details",
    ),
]

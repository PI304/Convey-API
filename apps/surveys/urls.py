from django.urls import path, URLPattern

from apps.surveys.views import SurveyListView, SurveyDetailView

urlpatterns: list[URLPattern] = [
    path("", SurveyListView.as_view(), name="survey_list"),
    path("/<int:pk>", SurveyDetailView.as_view(), name="survey_details"),
]

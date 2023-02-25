from django.urls import path

from apps.surveys.views import SurveyListView, SurveyDetailView

urlpatterns = [
    path("", SurveyListView.as_view(), name="survey_list"),
    path("<int:pk>", SurveyDetailView.as_view(), name="survey_details"),
]

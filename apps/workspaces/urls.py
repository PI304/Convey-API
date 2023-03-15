from django.urls import path, URLPattern
from apps.workspaces.views import (
    WorkspaceListView,
    WorkspaceDetailView,
    RoutineView,
    RoutineDetailCreateView,
    RoutineDetailView,
    WorkspaceAddSurveyPackageView,
    WorkspaceDestroySurveyPackageView,
)

urlpatterns: list[URLPattern] = [
    path("", WorkspaceListView.as_view(), name="workspace_list"),
    path("/<int:pk>", WorkspaceDetailView.as_view(), name="workspace_details"),
    path("/<int:pk>/routines", RoutineView.as_view(), name="routine"),
    path(
        "/<int:pk>/survey-packages/<int:survey_package_id>",
        WorkspaceDestroySurveyPackageView.as_view(),
        name="survey_removal",
    ),
    path(
        "/<int:pk>/survey-packages",
        WorkspaceAddSurveyPackageView.as_view(),
        name="survey_addition",
    ),
    path(
        "/routines/<int:pk>/routine-details",
        RoutineDetailCreateView.as_view(),
        name="routine_details",
    ),
    path(
        "/routine-details/<int:pk>", RoutineDetailView.as_view(), name="routine_details"
    ),
]

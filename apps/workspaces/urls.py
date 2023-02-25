from django.urls import path, URLPattern
from apps.workspaces.views import WorkspaceListView, WorkspaceDestroyView, RoutineView

urlpatterns: list[URLPattern] = [
    path("", WorkspaceListView.as_view(), name="workspace_list"),
    path("<int:pk>/", WorkspaceDestroyView.as_view(), name="workspace_details"),
    path("<int:pk>/routines/", RoutineView.as_view(), name="routine"),
]

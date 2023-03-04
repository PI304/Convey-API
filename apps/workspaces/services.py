from typing import List, Union

from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.survey_packages.models import SurveyPackage
from apps.workspaces.models import Routine, Workspace, WorkspaceComposition
from apps.workspaces.serializers import (
    RoutineDetailSerializer,
    WorkspaceCompositionSerializer,
)


class RoutineService(object):
    def __init__(self, routine: Union[Routine, int]):
        if type(routine) == int:
            self.routine = get_object_or_404(Routine, id=routine)
        else:
            self.routine = routine

    def add_routine_details(self, routine_details: List[dict]):
        for r in routine_details:
            survey_package_id = r.get("survey_package", None)
            if not survey_package_id:
                raise ValidationError(
                    "survey package id should be provided for all routine details"
                )
            del r["survey_package"]
            s = RoutineDetailSerializer(data=r)
            if s.is_valid(raise_exception=True):
                s.save(survey_package_id=survey_package_id, routine_id=self.routine.id)

        return self.routine


class WorkspaceService(object):
    def __init__(self, workspace: Union[Workspace, int]):
        if type(workspace) == int:
            self.workspace = get_object_or_404(Workspace, id=workspace)
        else:
            self.workspace = workspace

    def add_survey_packages(self, package_ids: list[int]):
        for pid in package_ids:
            try:
                package = get_object_or_404(SurveyPackage, id=pid)
            except Http404:
                raise ValidationError(f"invalid package id: {pid}")

            serializer = WorkspaceCompositionSerializer(data={})
            if serializer.is_valid(raise_exception=True):
                serializer.save(survey_package_id=pid, workspace_id=self.workspace.id)

        self.workspace.refresh_from_db()
        return self.workspace

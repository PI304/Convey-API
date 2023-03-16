from typing import List, Union

from django.http import Http404
from django.shortcuts import get_object_or_404

from apps.survey_packages.models import SurveyPackage
from apps.workspaces.models import Routine, Workspace, WorkspaceComposition
from apps.workspaces.serializers import (
    RoutineDetailSerializer,
    WorkspaceCompositionSerializer,
)
from config.exceptions import InstanceNotFound, ConflictException, InvalidInputException


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
                raise InvalidInputException(
                    "survey package id should be provided for all routine details"
                )
            try:
                in_workspace = get_object_or_404(
                    WorkspaceComposition,
                    survey_package_id=survey_package_id,
                    workspace_id=self.routine.workspace_id,
                )
            except Http404:
                raise InstanceNotFound(
                    f"survey package with the id {survey_package_id} does not exist or is not included in workspace"
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
                raise InstanceNotFound(f"invalid package id: {pid}")

            try:
                existing_composition = get_object_or_404(
                    WorkspaceComposition,
                    survey_package_id=pid,
                    workspace_id=self.workspace.id,
                )
                raise ConflictException(
                    f"survey package of id {pid} is already included in this workspace"
                )
            except Http404:
                pass

            serializer = WorkspaceCompositionSerializer(data={})
            if serializer.is_valid(raise_exception=True):
                serializer.save(survey_package_id=pid, workspace_id=self.workspace.id)

        self.workspace.refresh_from_db()
        return self.workspace

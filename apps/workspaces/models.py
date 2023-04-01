import shortuuid
from django.db import models

from apps.users.models import User
from apps.survey_packages.models import SurveyPackage
from config.mixins import TimeStampMixin


class Workspace(TimeStampMixin):
    id = models.BigAutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=30)
    uuid = models.CharField(max_length=22, null=False)
    access_code = models.CharField(max_length=128, null=False)

    class Meta:
        db_table = "workspace"

    def __str__(self):
        return f"[{self.id}] {self.name}"

    def __repr__(self):
        return f"Workspace({self.id}, {self.name})"


class WorkspaceComposition(TimeStampMixin):
    id = models.BigAutoField(primary_key=True)
    survey_package = models.ForeignKey(
        "survey_packages.SurveyPackage", on_delete=models.CASCADE
    )
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="survey_packages"
    )

    class Meta:
        db_table = "workspace_composition"

    def __str__(self):
        return f"[{self.id}] workspace: {self.workspace_id}/package: {self.survey_package_id}"

    def __repr__(self):
        return f"WorkspaceComposition({self.id}, {self.workspace_id}-{self.survey_package_id})"


class Routine(TimeStampMixin):
    id = models.BigAutoField(primary_key=True)
    workspace = models.OneToOneField(
        Workspace, on_delete=models.CASCADE, related_name="routine"
    )
    duration = models.IntegerField(null=False)
    kick_off = models.ForeignKey(
        SurveyPackage, on_delete=models.SET_NULL, null=True, related_name="kick_off_for"
    )

    class Meta:
        db_table = "routine"

    def __str__(self):
        return f"[{self.id}] workspace: {self.workspace_id}"

    def __repr__(self):
        return f"Routine({self.id}, {self.workspace_id})"


class RoutineDetail(TimeStampMixin):
    id = models.BigAutoField(primary_key=True)
    routine = models.ForeignKey(
        Routine, on_delete=models.CASCADE, related_name="routines"
    )
    nth_day = models.PositiveSmallIntegerField(null=False)
    time = models.CharField(max_length=5, null=False)
    survey_package = models.ForeignKey(
        SurveyPackage, on_delete=models.CASCADE, null=True
    )
    external_resource = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = "routine_detail"

    def __str__(self):
        return f"[{self.id}] routine: {self.routine_id}/nth_day: {self.nth_day}"

    def __repr__(self):
        return f"RoutineDetail({self.id}, {self.routine_id}-{self.nth_day})"

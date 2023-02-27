from typing import List, Union

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.workspaces.models import Routine
from apps.workspaces.serializers import RoutineDetailSerializer


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

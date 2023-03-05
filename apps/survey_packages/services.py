from typing import Union, List

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.survey_packages.models import SurveyPackage, PackagePart, PackageSubjectSurvey
from apps.survey_packages.serializers import (
    PackageContactSerializer,
    PackagePartSerializer,
    PackageSubjectSerializer,
    PackageSubjectSurveySerializer,
)


class SurveyPackageService(object):
    def __init__(self, package: Union[SurveyPackage, int]):
        if type(package) == int:
            self.package = get_object_or_404(SurveyPackage, id=package)
        else:
            self.package = package

    def add_contacts(self, contacts: List[dict]) -> SurveyPackage:
        if type(contacts) != list:
            raise ValidationError("'contacts' field must be a list")

        for c in contacts:
            serializer = PackageContactSerializer(data=c)
            if serializer.is_valid(raise_exception=True):
                serializer.save(survey_package_id=self.package.id)

        return self.package

    def delete_related_components(self) -> None:
        PackagePart.objects.filter(survey_package_id=self.package.id).delete()

    def create_parts(self, data: list[dict], package_id: int) -> list[PackagePart]:
        created_parts = []
        for d in data:
            part = self.create_part(d, package_id=package_id)
            created_parts.append(part)

        return created_parts

    def create_part(self, part_data: dict, package_id: int) -> PackagePart:
        # Create a part
        if "title" not in part_data or part_data["title"] is None:
            raise ValidationError("a part should have a title")

        serializer = PackagePartSerializer(data=dict(title=part_data["title"]))
        if serializer.is_valid(raise_exception=True):
            part = serializer.save(survey_package_id=package_id)

        # Create subjects
        if "subjects" not in part_data or part_data["subjects"] is None:
            raise ValidationError("a part should have a title")
        self._create_subjects(part_data["subjects"], part.id)

        part.refresh_from_db()

        return part

    def _create_subjects(self, subjects_list: list[dict], part_id: int):
        for subject in subjects_list:
            serializer = PackageSubjectSerializer(data=subject)
            if serializer.is_valid(raise_exception=True):
                serializer.save(package_part_id=part_id)

    @staticmethod
    def associate_subject_with_surveys(subject_id: int, data: list[dict]) -> None:
        for ss in data:
            serializer = PackageSubjectSurveySerializer(data=ss)
            if serializer.is_valid(raise_exception=True):
                serializer.save(subject_id=subject_id, survey_id=ss.get("survey", None))

    @staticmethod
    def delete_related_surveys(subject_id: int) -> None:
        PackageSubjectSurvey.objects.filter(subject_id=subject_id).delete()

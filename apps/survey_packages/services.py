from datetime import datetime
from typing import Union, List

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from rest_framework.exceptions import ValidationError

from apps.survey_packages.models import (
    SurveyPackage,
    PackagePart,
    PackageSubjectSurvey,
    Respondent,
)
from apps.survey_packages.serializers import (
    PackageContactSerializer,
    PackagePartSerializer,
    PackageSubjectSerializer,
    PackageSubjectSurveySerializer,
)
from apps.surveys.models import QuestionAnswer
from apps.workspaces.models import Workspace, RoutineDetail


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


class ResponseExportService(object):
    def __init__(self, workspace: Workspace, survey_package: SurveyPackage):
        self.workspace = workspace
        self.survey_package = survey_package
        self.respondents = None
        self.worksheet = None

    def base_data(self) -> list[Union[str, int]]:
        routine_id: int = self.workspace.routine.id
        routine_detail: RoutineDetail = RoutineDetail.objects.filter(
            routine_id=routine_id, survey_package_id=self.survey_package.id
        ).first()

        workspace_name: str = self.workspace.name
        package_name = self.survey_package.title
        nth_day = routine_detail.nth_day
        time = routine_detail.time

        return [workspace_name, package_name, nth_day, time]

    def _create_worksheet_template(self) -> Worksheet:
        wb: Workbook = Workbook()
        wb.title = f"{self.survey_package.title}_{datetime.now()}"
        ws: Worksheet = wb.active
        self.worksheet = ws

        self.worksheet.append(["워크스페이스", "설문 제목", "차시 (일)", "응답 지정 일시", "피험자ID"])
        respondent_list = self._set_respondents_list()

        i = 0
        for row in self.worksheet.iter_rows(
            min_row=1, min_col=6, max_col=6, max_row=len(respondent_list) + 1
        ):
            for cell in row:
                cell.value = respondent_list[i]
            i += 1

        return self.worksheet

    def _set_respondents_list(self) -> list[dict]:
        respondents: list[dict] = (
            Respondent.objects.filter(
                survey_package_id=self.survey_package.id, workspace_id=self.workspace.id
            )
            .order_by("respondent_id")
            .defer("respondent_id")
            .all()
        )
        self.respondents = respondents

        return self.respondents

    def _add_sector_data(self, sector_data, prefix):
        questions = sector_data.get("questions")
        sorted_questions = sorted(questions, key=lambda d: d["number"])
        i = 0
        for question in questions:
            col_char = chr(i + 70)
            if self.worksheet[f"{col_char}1"].value is None:
                self.worksheet[f"{col_char}1"] = f"{prefix}-{question.number}"

            # TODO: 하나의 문제, 여러명 respondent (하나의 열 안에서 respondent 행 만들기)
            answers: QuerySet = (
                QuestionAnswer.objects.filter(question_id=question["id"])
                .order_by("respondent_id")
                .all()
            )

            row = 1
            for answer in answers:
                self.worksheet[f"{col_char}{row}"] = answer["answer"]
                row += 1

            i += 1

    def _add_survey_data(self, survey_data, prefix):
        prefix = f"{prefix}-{survey_data.get('abbr')}"
        sectors = survey_data.get("sectors")

        for sector in sectors:
            self._add_sector_data(sector, prefix)

    def _add_subject_data(self, subject_data, prefix):
        prefix = f"{prefix}-{subject_data.get('number')}"

        for survey in subject_data.get("surveys"):
            self._add_survey_data(survey, prefix)

    def _add_part_data(self, part_data: dict):
        prefix = part_data.get("number")

        for subject in part_data.get("subjects"):
            self._add_subject_data(subject, prefix)

    def export_to_worksheet(self):
        parts: QuerySet = PackagePart.objects.filter(
            survey_package_id=self.survey_package.id
        ).all()
        data: list[dict] = PackagePartSerializer(parts, many=True).data

        print(data)

        for part in data:
            self._add_part_data(part)

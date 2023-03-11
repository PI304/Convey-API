from datetime import datetime
from typing import Union, List

import openpyxl.utils.cell
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
        self.workbook = None
        self.worksheet = None
        self._col_num = 6

    def _base_data(self) -> list[Union[str, int]]:
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
        self.workbook = wb
        ws: Worksheet = wb.active
        self.worksheet = ws

        self.worksheet.append(["워크스페이스", "설문 제목", "차시 (일)", "응답 지정 일시", "피험자ID"])
        self.worksheet.append(self._base_data())
        respondent_list = self._set_respondents_list()

        i = 0
        for row in self.worksheet.iter_rows(
            min_row=2, min_col=5, max_col=5, max_row=len(respondent_list) + 1
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
            .all()
            .values_list("respondent_id", flat=True)
        )
        self.respondents = respondents

        return self.respondents

    def _add_sector_data(self, sector_data, prefix):
        question_type = sector_data.get("question_type")
        print(question_type)
        questions = sector_data.get("questions")
        sorted_questions = sorted(questions, key=lambda d: d["number"])

        for question in sorted_questions:
            col_letter = openpyxl.utils.cell.get_column_letter(self._col_num)

            # bread crumb format question number
            if self.worksheet[f"{col_letter}1"].value is None:
                formatted_question_number = str(question.get("number"))
                print(formatted_question_number)
                if formatted_question_number[-1] != "0":
                    formatted_question_number = formatted_question_number.replace(
                        ".", "-"
                    )
                else:
                    dot_index = formatted_question_number.index(".")
                    formatted_question_number = formatted_question_number[:dot_index]

                self.worksheet[
                    f"{col_letter}1"
                ] = f"{prefix}-{formatted_question_number}"

            answers: QuerySet = (
                QuestionAnswer.objects.filter(question_id=question["id"])
                .order_by("respondent_id")
                .values()
            )

            if len(self.respondents) != len(answers):
                raise ValidationError("something went wrong")

            row = 2
            for answer in answers:
                answer_val = answer["answer"]
                if "$" in answer_val:
                    answer_val = answer_val.replace("$", ", ")

                if question_type in ["likert", "extent", "single_select"]:
                    try:
                        answer_val = int(answer_val)
                        self.worksheet[f"{col_letter}{row}"].number_format = "0"
                        self.worksheet[f"{col_letter}{row}"].value = answer_val
                    except Exception:
                        pass

                self.worksheet[f"{col_letter}{row}"] = answer_val

                row += 1

            self._col_num += 1

    def _add_survey_data(self, survey_data, prefix):
        if survey_data.get("number"):
            prefix = f"{prefix}-{survey_data.get('number')}"

        survey = survey_data.get("survey")
        prefix = f"{prefix}-{survey.get('abbr')}"

        sectors = survey.get("sectors")

        for sector in sectors:
            self._add_sector_data(sector, prefix)

    def _add_subject_data(self, subject_data):
        prefix = f"{subject_data.get('number')}"
        for survey in subject_data.get("surveys"):
            self._add_survey_data(survey, prefix)

    def _add_part_data(self, part_data: dict):
        for subject in part_data.get("subjects"):
            self._add_subject_data(subject)

    def export_to_worksheet(self):
        self._create_worksheet_template()

        parts: QuerySet = PackagePart.objects.filter(
            survey_package_id=self.survey_package.id
        ).all()
        data: list[dict] = PackagePartSerializer(parts, many=True).data

        print(data)

        for part in data:
            self._add_part_data(part)

        return self.workbook

from typing import Union

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.surveys.models import (
    Survey,
    SurveySector,
    SectorQuestion,
    ChoicesSet,
    QuestionChoice,
)
from apps.surveys.serializers import (
    SurveySectorSerializer,
    SectorQuestionSerializer,
    QuestionChoiceSerializer,
    ChoicesSetSerializer,
)


class SurveyService(object):
    def __init__(self, survey: Union[Survey, int]):
        if type(survey) == int:
            self.survey = get_object_or_404(Survey, id=survey)
        else:
            self.survey = survey

    def create_sectors(self, sectors: list[dict]) -> list[SurveySector]:
        created_sectors: list[SurveySector] = []

        for data in sectors:
            sector = self._create_sector(data)
            created_sectors.append(sector)

        return created_sectors

    def _make_common_choices(self, common_choices_list: list[dict]) -> list[int]:
        common_choices = []
        for c in common_choices_list:
            serializer = QuestionChoiceSerializer(data=c)
            if serializer.is_valid(raise_exception=True):
                choice = serializer.save()
                common_choices.append(choice.id)
        return common_choices

    def _make_question(self, question_data: dict, sector_id: int):
        # Create a question with empty choices
        question = None
        serializer = SectorQuestionSerializer(data=question_data)
        if serializer.is_valid(raise_exception=True):
            question = serializer.save(sector_id=sector_id)

        return question

    def _make_choices(self, choices_list_data: list[dict]) -> list[int]:
        choices_id_list = []
        for c_data in choices_list_data:
            serializer = QuestionChoiceSerializer(data=c_data)
            if serializer.is_valid(raise_exception=True):
                choice = serializer.save()
                choices_id_list.append(choice.id)

        return choices_id_list

    def _make_choices_set(
        self, choices_id_list: list[int], question_id: int
    ) -> list[ChoicesSet]:
        choices_set: list[ChoicesSet] = []
        for cid in choices_id_list:
            serializer = ChoicesSetSerializer(
                data=dict(choice_id=cid, question_id=question_id)
            )
            if serializer.is_valid(raise_exception=True):
                c_set = serializer.save()
                choices_set.append(c_set)

        return choices_set

    def _create_sector(self, data: dict) -> SurveySector:
        # Create base SurveySector
        sector_data = dict(
            title=data.get("title", None),
            description=data.get("description", None),
            question_type=data.get("question_type", None),
        )

        sector = None

        serializer = SurveySectorSerializer(data=sector_data)
        if serializer.is_valid(raise_exception=True):
            sector = serializer.save(survey_id=self.survey.id)

        # Create common choices if exists
        common_choices = None
        if "common_choices" in data:
            common_choices: list[int] = self._make_common_choices()

        # Create Questions and associate with survey sector
        questions_list_data: list[dict] = data.get("questions", None)
        if not questions_list_data:
            raise ValidationError("'questions' field is required")

        for q in questions_list_data:
            # Create a question with empty choices
            question: SectorQuestion = self._make_question(q, sector.id)

            # if common choices are present
            if common_choices:
                common_choices_set = self._make_choices_set(common_choices, question.id)
            # no common choices
            else:
                # make choices and set
                choices_list_data = q.get("choices", None)
                if choices_list_data is None:
                    raise ValidationError(
                        "'choices' must be set for a non-common-choice question"
                    )

                choices = self._make_choices(choices_list_data)
                choices_set = self._make_choices_set(choices, question.id)

        return sector

    def delete_related_sectors(self) -> None:
        sectors: list[SurveySector] = SurveySector.objects.filter(
            survey_id=self.survey.id
        )
        if sectors:
            for s in sectors:
                s.delete()

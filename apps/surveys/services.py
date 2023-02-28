from typing import Union

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from apps.surveys.models import Survey, SurveySector
from apps.surveys.serializers import (
    SurveySectorSerializer,
    SectorChoiceSerializer,
    SectorQuestionSerializer,
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

    def _create_sector(self, data: dict) -> SurveySector:
        # Create base SurveySector
        sector_data = dict(
            title=data.get("title", None),
            description=data.get("description", None),
            question_type=data.get("question_type", None),
        )

        serializer = SurveySectorSerializer(data=sector_data)
        if serializer.is_valid(raise_exception=True):
            sector = serializer.save(survey_id=self.survey.id)

        # Create Choices and associate with survey sector
        choices_list_data: list[dict] = data.get("choices", None)
        if not choices_list_data:
            raise ValidationError("'choices' field is required")

        for c in choices_list_data:
            choice_data = dict(key=c.get("key", None), value=c.get("value", None))
            serializer = SectorChoiceSerializer(data=choice_data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(sector_id=sector.id)

        # Create Questions and associate with survey sector
        questions_list_data: list[dict] = data.get("questions", None)
        if not questions_list_data:
            raise ValidationError("'questions' field is required")

        for q in questions_list_data:
            serializer = SectorQuestionSerializer(data=q)
            if serializer.is_valid(raise_exception=True):
                serializer.save(sector_id=sector.id)

        return sector

    def delete_related_sectors(self) -> None:
        sectors: list[SurveySector] = SurveySector.objects.filter(
            survey_id=self.survey.id
        )
        if sectors:
            for s in sectors:
                s.delete()

import json
import pytest
from django.shortcuts import get_object_or_404

from apps.surveys.models import Survey
from apps.surveys.services import SurveyService
from apps.base_fixtures import *


@pytest.fixture(autouse=False, scope="function")
def sample_sector_data():
    try:
        file_path = "./apps/surveys/tests/sample_data/sample_sector.json"
        with open(file_path, "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        file_path = "tests/sample_data/sample_sector.json"
        with open(file_path, "r") as file:
            data = json.load(file)
            return data


@pytest.fixture(autouse=False, scope="function")
def create_empty_survey(db):
    Survey.objects.create(
        id=999,
        title="test survey 1",
        description="make empty survey",
        abbr="test",
        author_id=999,
    )
    Survey.objects.create(
        id=998,
        title="test survey 2",
        description="make empty survey",
        abbr="test2",
        author_id=999,
    )


@pytest.fixture(autouse=False, scope="function")
def create_sectors(db, sample_sector_data):
    survey = get_object_or_404(Survey, id=999)

    service = SurveyService(survey)
    service.delete_related_sectors()

    data = sample_sector_data
    service.create_sectors(data)

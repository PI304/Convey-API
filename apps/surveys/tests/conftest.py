import json
import os

import pytest

from apps.surveys.models import Survey, SurveySector, SectorChoice, SectorQuestion
from apps.users.models import User
from config.client_request_for_test import ClientRequest
from rest_framework.test import APIClient


@pytest.fixture(autouse=False, scope="function")
def sample_sector_data():
    file_path = "./apps/surveys/tests/sample_sector.json"
    with open(file_path, "r") as file:
        data = json.load(file)
        return data


@pytest.fixture(autouse=True, scope="session")
@pytest.mark.django_db
def client_request(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        user = User.objects.create(
            id=999, email="email@test.com", name="test", password="12345678", role=0
        )
        client = APIClient()
        client.force_authenticate(user)
        return ClientRequest(client)


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
def create_sectors(db):
    # Sector 1
    SurveySector.objects.create(
        id=999,
        survey_id=999,
        title="sector 1",
        description="sector 1",
        question_type="likert",
    )

    SectorChoice.objects.create(id=999, sector_id=999, key="1", value="매우 그렇다")
    SectorChoice.objects.create(id=998, sector_id=999, key="2", value="그렇다")
    SectorChoice.objects.create(id=997, sector_id=999, key="3", value="보통이다")
    SectorChoice.objects.create(id=996, sector_id=999, key="4", value="그렇지 않다")
    SectorChoice.objects.create(id=995, sector_id=999, key="5", value="매우 그렇지 않다")

    SectorQuestion.objects.create(id=999, sector_id=999, content="질문1")
    SectorQuestion.objects.create(id=998, sector_id=999, content="질문2")
    SectorQuestion.objects.create(id=997, sector_id=999, content="질문3")

    # Sector 2
    SurveySector.objects.create(
        id=998,
        survey_id=999,
        title="sector 2",
        description="sector 2",
        question_type="short_answer",
    )

    SectorChoice.objects.create(id=994, sector_id=998, key="일주일에", value="%d일")
    SectorChoice.objects.create(id=993, sector_id=998, key="하루에", value="%d시간%d분")

    SectorQuestion.objects.create(
        id=996, sector_id=998, content="한번에 적어도 10분 이상 걸은 날은 며칠?"
    )
    SectorQuestion.objects.create(
        id=995, sector_id=998, content="그런 날 중 하루에 걸으면서 보낸 시간?"
    )

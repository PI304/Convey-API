import json
import pytest

from apps.base_fixtures import *
from apps.survey_packages.models import SurveyPackage, PackageContact
from apps.surveys.models import Survey, SurveySector, SectorChoice, SectorQuestion


@pytest.fixture(autouse=False, scope="function")
def sample_package_base_data():
    try:
        file_path = "./apps/survey_packages/tests/sample_data/base_package.json"
        with open(file_path, "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        file_path = "tests/sample_data/base_package.json"
        with open(file_path, "r") as file:
            data = json.load(file)
            return data


@pytest.fixture(autouse=False, scope="function")
def create_empty_survey_packages(db):
    SurveyPackage.objects.create(
        id=999,
        title="test survey package 1",
        description="make empty survey package",
        access_code="12345678",
        manager="z9",
        author_id=999,
    )
    SurveyPackage.objects.create(
        id=998,
        title="test survey package 2",
        description="make empty survey package",
        access_code="12345678",
        manager="z9",
        author_id=999,
    )

    PackageContact.objects.create(
        id=999, type="email", content="someemail@example.com", survey_package_id=999
    )
    PackageContact.objects.create(
        id=998, type="phone", content="01011112222", survey_package_id=999
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

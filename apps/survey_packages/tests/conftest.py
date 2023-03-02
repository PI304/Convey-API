import json
import pytest

from apps.base_fixtures import *
from apps.survey_packages.models import SurveyPackage, PackageContact


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
def sample_package_parts_data():
    try:
        file_path = "./apps/survey_packages/tests/sample_data/survey_parts.json"
        with open(file_path, "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        file_path = "tests/sample_data/survey_parts.json"
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

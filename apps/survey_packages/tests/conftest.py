import json
import pytest
from django.shortcuts import get_object_or_404

from apps.base_fixtures import *
from apps.surveys.tests.conftest import create_empty_survey
from apps.survey_packages.models import SurveyPackage, PackageContact
from apps.survey_packages.serializers import SurveyPackageSerializer
from apps.survey_packages.services import SurveyPackageService


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
        file_path = "./apps/survey_packages/tests/sample_data/survey_package_parts.json"
        with open(file_path, "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        file_path = "tests/sample_data/survey_package_parts.json"
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
def compose_empty_survey_package(db, sample_package_parts_data):
    package = get_object_or_404(SurveyPackage, id=999)

    service = SurveyPackageService(package)
    service.delete_related_components()

    parts = service.create_parts(sample_package_parts_data, 999)

import json
import pytest

from apps.base_fixtures import *
from apps.surveys.tests.conftest import *
from apps.survey_packages.models import (
    SurveyPackage,
    PackageContact,
    PackagePart,
    PackageSubject,
    PackageSubjectSurvey,
)
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
def compose_empty_survey_package(
    db, sample_package_parts_data, create_empty_survey, create_sectors
):
    package = get_object_or_404(SurveyPackage, id=999)

    service = SurveyPackageService(package)
    service.delete_related_components()

    PackagePart.objects.create(id=999, title="기초 설문", survey_package_id=999)
    PackagePart.objects.create(id=998, title="디지털 일상", survey_package_id=999)

    PackageSubject.objects.create(
        id=999, number=1, title="사회 정서 발달", package_part_id=999
    )
    PackageSubject.objects.create(id=998, number=2, title="가족", package_part_id=999)
    PackageSubject.objects.create(id=997, number=3, title="스트레스", package_part_id=998)
    PackageSubject.objects.create(id=996, number=4, title="수면", package_part_id=998)

    PackageSubjectSurvey.objects.create(
        id=999, number=1, title="기질/환경민감성", survey_id=999, subject_id=999
    )
    PackageSubjectSurvey.objects.create(
        id=998, number=2, title="사회적 기술", survey_id=998, subject_id=999
    )
    PackageSubjectSurvey.objects.create(
        id=997, number=1, title="가족의 디지털 상호작용", survey_id=999, subject_id=998
    )
    PackageSubjectSurvey.objects.create(id=996, number=1, survey_id=999, subject_id=997)
    PackageSubjectSurvey.objects.create(id=995, number=1, survey_id=999, subject_id=996)


@pytest.fixture(autouse=False, scope="function")
def get_package_part_id(db):
    return PackagePart.objects.filter(title="기초 설문").first().id


@pytest.fixture(autouse=False, scope="function")
def get_package_subject_id(db):
    return PackageSubject.objects.filter(title="사회 정서 발달").first().id

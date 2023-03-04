import tempfile

import pytest
from PIL import Image

from apps.survey_packages.models import PackagePart, PackageSubject
from apps.surveys.models import Survey


@pytest.mark.django_db
def test_create_empty_survey_package(client_request, sample_package_base_data):
    url = "/api/survey-packages/"
    data = sample_package_base_data
    res = client_request("post", url, data)

    assert res.status_code == 201
    assert res.data["author"]["id"] == 999


@pytest.mark.django_db
def test_update_empty_package(client_request, create_empty_survey_packages):
    url = "/api/survey-packages/999/"
    data = dict(
        description="updated description",
        contacts=[dict(type="email", content="updated@email.com")],
    )

    res = client_request("patch", url, data)

    assert res.status_code == 200
    assert res.data["description"] == data["description"]
    assert len(res.data["contacts"]) == 1


@pytest.mark.django_db
def test_compose_survey_package(
    client_request,
    create_empty_survey_packages,
    sample_package_parts_data,
    create_empty_survey,
):
    url = "/api/survey-packages/999/"
    data = sample_package_parts_data
    res = client_request("put", url, data)

    assert res.status_code == 200
    assert res.data["id"] == 999
    assert res.data["author"]["id"] == 999
    assert len(res.data["contacts"]) == 2
    assert len(res.data["parts"]) == 2


@pytest.mark.django_db
def test_get_survey_package_by_id(
    client_request,
    create_empty_survey_packages,
    create_empty_survey,
    compose_empty_survey_package,
):
    url = "/api/survey-packages/999/"
    res = client_request("get", url)

    assert res.status_code == 200
    assert res.data["id"] == 999
    assert len(res.data["parts"]) == 2
    assert len(res.data["parts"][0]["subjects"]) == 2


@pytest.mark.django_db
def test_get_all_survey_packages(
    client_request, create_empty_survey, create_empty_survey_packages
):
    url = "/api/survey-packages/"
    res = client_request("get", url)

    assert res.status_code == 200
    assert len(res.data["results"]) == 2


@pytest.mark.django_db
def test_delete_survey_package(
    client_request,
    create_empty_survey,
    create_sectors,
    create_empty_survey_packages,
    compose_empty_survey_package,
):
    url = "/api/survey-packages/999/"
    res = client_request("del", url)

    remaining_surveys = Survey.objects.all().count()
    remaining_parts = PackagePart.objects.all().count()
    remaining_subjects = PackageSubject.objects.all().count()

    assert res.status_code == 204
    assert remaining_surveys == 2
    assert remaining_parts == 0
    assert remaining_subjects == 0

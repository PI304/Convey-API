import pytest

from apps.survey_packages.models import (
    PackagePart,
    PackageSubject,
    PackageSubjectSurvey,
)

base_url = "/api/survey-packages/parts/"


@pytest.mark.django_db
def test_get_all_subjects_under_package_part(
    client_request,
    create_empty_survey_packages,
    compose_empty_survey_package,
    get_package_part_id,
):
    url = base_url + f"{get_package_part_id}/subjects"
    res = client_request("get", url)

    assert res.status_code == 200
    assert len(res.data["results"]) == 2


@pytest.mark.django_db
def test_create_subject(
    client_request,
    create_empty_survey_packages,
    compose_empty_survey_package,
    get_package_part_id,
):
    part_id = get_package_part_id
    url = base_url + f"{part_id}/subjects"
    data = dict(number=3, title="학교")
    res = client_request("post", url, data)

    assert res.status_code == 201
    assert res.data["package_part"] == part_id


@pytest.mark.django_db
def test_get_subject_by_id(
    client_request,
    create_empty_survey_packages,
    compose_empty_survey_package,
    get_package_subject_id,
):
    subject_id = get_package_subject_id
    url = base_url + f"subjects/{subject_id}"
    res = client_request("get", url)

    assert res.status_code == 200
    assert res.data["id"] == subject_id
    assert len(res.data["surveys"]) == 2


@pytest.mark.django_db
def test_update_subject_title(
    client_request,
    create_empty_survey_packages,
    compose_empty_survey_package,
    get_package_subject_id,
):
    subject_id = get_package_subject_id
    url = base_url + f"subjects/{subject_id}"
    data = dict(title="사회 정서 발달 새제목")
    res = client_request("patch", url, data)

    assert res.status_code == 200
    assert res.data["id"] == subject_id
    assert res.data["title"] == data["title"]


@pytest.mark.django_db
def test_delete_part(
    client_request,
    create_empty_survey_packages,
    compose_empty_survey_package,
    get_package_subject_id,
):
    subject_id = get_package_subject_id

    url = base_url + f"subjects/{subject_id}"
    res = client_request("del", url)

    remaining_surveys = PackageSubjectSurvey.objects.all().count()

    assert res.status_code == 204
    assert remaining_surveys == 3


@pytest.mark.django_db
def test_compose_package_subject(
    client_request,
    create_empty_survey_packages,
    compose_empty_survey_package,
    get_package_subject_id,
):
    url = base_url + f"subjects/{get_package_subject_id}"
    data = [
        dict(number=1, title="기질/환경민감성 2", survey=998),
        dict(number=2, title="사회적 기술 2", survey=999),
    ]
    res = client_request("put", url, data)

    assert res.status_code == 200
    assert len(res.data["surveys"]) == 2
    assert res.data["surveys"][0]["survey"]["id"] == 998

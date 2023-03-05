import pytest

from apps.survey_packages.models import PackageSubject, PackagePart

base_url = "/api/survey-packages/"


@pytest.mark.django_db
def test_get_all_parts_under_survey_package(
    client_request,
    create_empty_survey_packages,
    compose_empty_survey_package,
):
    url = base_url + "999/parts/"
    res = client_request("get", url)

    assert res.status_code == 200
    assert len(res.data["results"]) == 2


@pytest.mark.django_db
def test_create_part(client_request, create_empty_survey_packages):
    url = base_url + "999/parts/"
    data = dict(
        title="기초 설문",
        subjects=[dict(number=1, title="사회 정서 발달"), dict(number=2, title="가족")],
    )
    res = client_request("post", url, data)

    assert res.status_code == 201
    assert len(res.data["subjects"]) == 2


@pytest.mark.django_db
def test_get_part_by_id(
    client_request,
    create_empty_survey_packages,
    compose_empty_survey_package,
    get_package_part_id,
):
    part_id = get_package_part_id

    url = base_url + f"parts/{part_id}/"
    res = client_request("get", url)

    assert res.status_code == 200
    assert res.data["id"] == part_id
    assert len(res.data["subjects"]) == 2


@pytest.mark.django_db
def test_update_part_title(
    client_request,
    create_empty_survey_packages,
    compose_empty_survey_package,
    get_package_part_id,
):
    part_id = get_package_part_id

    url = base_url + f"parts/{part_id}/"
    data = dict(title="기초 설문 새제목")
    res = client_request("patch", url, data)

    assert res.status_code == 200
    assert res.data["id"] == part_id
    assert res.data["title"] == data["title"]


@pytest.mark.django_db
def test_delete_part(
    client_request,
    create_empty_survey_packages,
    compose_empty_survey_package,
    get_package_part_id,
):
    part_id = get_package_part_id

    url = base_url + f"parts/{part_id}/"
    res = client_request("del", url)

    remaining_subjects = PackageSubject.objects.all().count()

    assert res.status_code == 204
    assert remaining_subjects == 2

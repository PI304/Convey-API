import pytest


@pytest.mark.django_db
def test_get_all_surveys(client_request, create_empty_survey):
    url = "/api/surveys/"
    res = client_request("get", url)

    assert res.status_code == 200
    assert len(res.data["results"]) == 2


@pytest.mark.django_db
def test_create_empty_survey(client_request):
    url = "/api/surveys/"
    data = dict(title="title", description="description", abbr="test")
    res = client_request("post", url, data)

    assert res.status_code == 201
    assert res.data["title"] == data["title"]
    assert res.data["author"]["id"] == 999


@pytest.mark.django_db
def test_update_empty_survey(create_empty_survey, client_request):
    url = "/api/surveys/999/"
    data = dict(description="updated", abbr="t")
    res = client_request("patch", url, data)

    print(res.data)

    assert res.status_code == 200
    assert res.data["description"] == data["description"]
    assert res.data["abbr"] == data["abbr"]
    assert res.data["updated_at"] is not None


@pytest.mark.django_db
def test_compose_empty_survey(client_request, create_empty_survey, sample_sector_data):
    url = "/api/surveys/999/"
    data = sample_sector_data
    res = client_request("put", url, data)

    print(res.data)
    assert res.status_code == 200
    assert res.data["title"] == "test survey 1"
    assert len(res.data["sectors"]) == 2
    assert len(res.data["sectors"][0]["common_choices"]) == 5

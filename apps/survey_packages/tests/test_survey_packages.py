import tempfile

import pytest
from PIL import Image
from rest_framework.test import APIRequestFactory, APIClient


@pytest.mark.django_db
def test_create_empty_survey_package(client_json_request, sample_package_base_data):
    url = "/api/survey-packages/"
    data = sample_package_base_data
    res = client_json_request("post", url, data)

    assert res.status_code == 201
    assert res.data["author"]["id"] == 999


@pytest.mark.django_db
def test_update_empty_package(client_json_request, create_empty_survey_packages):
    url = "/api/survey-packages/999/"
    data = dict(
        description="updated description",
        contacts=[dict(type="email", content="updated@email.com")],
    )

    res = client_json_request("patch", url, data)

    assert res.status_code == 200
    assert res.data["description"] == data["description"]
    assert len(res.data["contacts"]) == 1

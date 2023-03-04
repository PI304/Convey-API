import pytest
from django.shortcuts import get_object_or_404

from apps.workspaces.models import RoutineDetail, Workspace


@pytest.mark.django_db
def test_create_workspace(client_request):
    url = "/api/workspaces/"
    data = dict(name="workspace1", access_code="12345678")
    res = client_request("post", url, data)

    assert res.status_code == 201
    assert res.data["owner"] == 999
    assert len(res.data["uuid"]) == 22


@pytest.mark.django_db
def test_get_workspaces_by_request_user(client_request, create_workspaces):
    url = "/api/workspaces/"
    res = client_request("get", url)

    assert res.status_code == 200
    assert len(res.data) == 2


@pytest.mark.django_db
def test_create_workspace_routine(
    client_request,
    create_workspaces,
    create_empty_survey_packages,
    sample_routines_data,
):
    url = "/api/workspaces/999/routines/"
    data = sample_routines_data
    res = client_request("post", url, data)

    print(res.content)
    assert res.status_code == 201
    assert res.data["workspace"]["id"] == 999
    assert len(res.data["routines"]) == 2
    assert res.data["kick_off"] == 999


@pytest.mark.django_db
def test_get_workspace_routine(
    client_request, create_workspaces, create_workspace_routine
):
    url = "/api/workspaces/999/routines/"
    res = client_request("get", url)

    assert res.status_code == 200
    assert res.data["workspace"]["id"] == 999
    assert len(res.data["routines"]) == 2
    assert res.data["kick_off"] == 999


@pytest.mark.django_db
def test_get_workspace_by_id(client_request, create_workspaces):
    url = "/api/workspaces/999/"
    res = client_request("get", url)

    assert res.status_code == 200
    assert res.data["owner"] == 999
    assert len(res.data["uuid"]) == 22


@pytest.mark.django_db
def test_create_routine_details(
    client_request, create_workspaces, create_workspace_routine
):
    url = "/api/workspaces/routine-details/"
    data = dict(routine=999, nth_day=1, time="12:00", survey_package=998)
    res = client_request("post", url, data)

    routine_count = RoutineDetail.objects.filter(routine_id=999).count()

    assert res.status_code == 201
    assert routine_count == 3


@pytest.mark.django_db
def test_get_routine_detail_by_id(
    client_request, create_workspaces, create_workspace_routine
):
    url = "/api/workspaces/routine-details/999/"
    res = client_request("get", url)

    assert res.status_code == 200
    assert res.data["time"] == "09:00"


@pytest.mark.django_db
def test_add_survey_packages_to_workspace(
    client_request, create_workspaces, create_empty_survey_packages
):
    url = "/api/workspaces/999/survey-packages/"
    data = dict(survey_packages=[999, 998])
    res = client_request("post", url, data)

    print(res.content)
    assert res.status_code == 201
    assert len(res.data["survey_packages"]) == 2


@pytest.mark.django_db
def test_remove_survey_package_from_workspace(
    client_request, create_workspaces, add_survey_packages_to_workspace
):
    url = "/api/workspaces/survey-packages/999/"
    res = client_request("del", url)

    print(res.content)

    assert res.status_code == 200
    assert len(res.data["survey_packages"]) == 1


@pytest.mark.django_db
def test_get_kick_off_survey_package(
    client_request,
    create_empty_survey_packages,
    create_empty_survey,
    create_sectors,
    compose_empty_survey_package,
    create_workspaces,
    create_workspace_routine,
    add_survey_packages_to_workspace,
):
    workspace = get_object_or_404(Workspace, id=999)
    url = f"/api/survey-packages/kick-off/?key={workspace.uuid}someuuidforrespondent&code={workspace.access_code}"
    res = client_request("get", url)

    assert res.status_code == 200
    assert res.data["workspace"] == 999
    assert len(res.data["survey_package"]["parts"]) == 2

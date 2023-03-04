import json

import shortuuid

from apps.base_fixtures import *
from apps.surveys.tests.conftest import *
from apps.survey_packages.tests.conftest import *
from apps.workspaces.models import (
    Workspace,
    Routine,
    RoutineDetail,
    WorkspaceComposition,
)


@pytest.fixture(autouse=False, scope="function")
def create_workspaces(db):
    Workspace.objects.create(
        id=999,
        name="workspace1",
        access_code="12345678",
        owner_id=999,
        uuid=shortuuid.uuid(),
    )
    Workspace.objects.create(
        id=998,
        name="workspace2",
        access_code="12345678",
        owner_id=999,
        uuid=shortuuid.uuid(),
    )


@pytest.fixture(autouse=False, scope="function")
def create_workspace_routine(db, create_empty_survey_packages):
    Routine.objects.create(id=999, workspace_id=999, duration=2, kick_off_id=999)
    RoutineDetail.objects.create(
        id=999, routine_id=999, nth_day=1, time="09:00", survey_package_id=999
    )
    RoutineDetail.objects.create(
        id=998, routine_id=999, nth_day=2, time="09:00", survey_package_id=998
    )


@pytest.fixture(autouse=False, scope="function")
def sample_routines_data():
    try:
        file_path = "./apps/workspaces/tests/sample_data/routines.json"
        with open(file_path, "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        file_path = "tests/sample_data/routines.json"
        with open(file_path, "r") as file:
            data = json.load(file)
            return data


@pytest.fixture(autouse=False, scope="function")
def add_survey_packages_to_workspace(create_empty_survey_packages):
    WorkspaceComposition.objects.create(id=999, survey_package_id=999, workspace_id=999)
    WorkspaceComposition.objects.create(id=998, survey_package_id=998, workspace_id=999)

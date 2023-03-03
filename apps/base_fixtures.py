import pytest

from config.client_request_for_test import ClientRequest
from rest_framework.test import APIClient

from apps.users.models import User


@pytest.fixture(autouse=True, scope="session")
@pytest.mark.django_db
def client_request(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        user = User.objects.create(
            id=999, email="email@test.com", name="test", password="12345678", role=0
        )
        client = APIClient()
        client.force_authenticate(user)
        return ClientRequest(client)

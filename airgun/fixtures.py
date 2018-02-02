import pytest

from airgun.session import Session


@pytest.fixture()
def session(request):
    return Session(request.module.__name__)

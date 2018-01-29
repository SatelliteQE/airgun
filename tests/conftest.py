import pytest

from base.session import Session


@pytest.fixture(autouse=True)
def session(request):
    return Session(request.module.__name__)

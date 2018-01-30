import pytest

from airgun import settings
from airgun.session import Session


@pytest.fixture(autouse=True)
def session(request):
    return Session(request.module.__name__)


def pytest_collection_modifyitems(items, config):
    """ called after collection has been performed, may filter or re-order
    the items in-place.
    """
    if not settings.configured:
        settings.configure()

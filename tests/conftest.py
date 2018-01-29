import os
import pytest

from base.session import Session


@pytest.fixture(autouse=True)
def session():
    # fixme: needs testsing for compatibility with xdist
    return Session(os.environ['PYTEST_CURRENT_TEST'])
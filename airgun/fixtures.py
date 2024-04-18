"""Handy fixtures which you may want to use in your tests.

Just add the following line into your `conftest.py`::

    pytest_plugins = ["airgun.fixtures"]

"""

import pytest

from airgun.session import Session


@pytest.fixture()
def session(request):
    """Session fixture which automatically initializes (but does not start!)
    airgun UI session and correctly passes current test name to it.


    Usage::

        def test_foo(session):
            with session:
                # your ui test steps here
                session.architecture.create({'name': 'bar'})

    """
    test_name = f'{request.module.__name__}.{request.node.name}'
    return Session(test_name)


@pytest.fixture()
def autosession(request):
    """Session fixture which automatically initializes and starts airgun UI
    session and correctly passes current test name to it. Use it when you want
    to have a session started before test steps and closed after all of them,
    i.e. when you don't need manual control over when the session is started or
    closed.

    Usage::

        def test_foo(autosession):
            # your ui test steps here
            autosession.architecture.create({'name': 'bar'})

    """
    test_name = f'{request.module.__name__}.{request.node.name}'
    with Session(test_name) as started_session:
        yield started_session

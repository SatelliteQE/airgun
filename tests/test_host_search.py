from functools import cached_property
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from wait_for import TimedOutError, wait_for

from airgun.views import common
from airgun.views.all_hosts import AllHostsTableView
from airgun.views.host import HostsView


class SearchTable:
    """Model a header snapshot retained while React replaces the table."""

    def __init__(self, states, initial=None):
        self.states = iter(states)
        self.state = initial or ((None,), [{0: False}])
        self.cache_clears = 0

    @cached_property
    def headers(self):
        if isinstance(self.state, Exception):
            raise self.state
        return self.state[0]

    def clear_cache(self):
        self.__dict__.pop('headers', None)
        self.cache_clears += 1
        self.state = next(self.states, self.state)

    def read(self):
        if isinstance(self.state[1], Exception):
            raise self.state[1]
        return self.state[1]


@pytest.fixture(params=[HostsView, AllHostsTableView], ids=['hosts', 'all-hosts'])
def search_view(request):
    class SearchView:
        table = None

        def is_searchable(self):
            return True

        def _read_search_results(self, query=None):
            if query is None:
                return request.param._read_search_results(self)
            return request.param._read_search_results(self, query)

    view = SearchView()
    view._HOST_SEARCH_STATE = getattr(request.param, '_HOST_SEARCH_STATE', '')
    view.searchbox = SimpleNamespace(search=Mock())
    view.responses = iter([['target.example.com']])
    view.response = None

    def execute_script(script, *args):
        if args and args[-1] is False:
            view.response = next(view.responses, view.response)
            return view.response
        return None

    view.browser = SimpleNamespace(
        plugin=SimpleNamespace(ensure_page_safe=Mock()),
        wait_for_element=Mock(return_value=True),
        execute_script=Mock(side_effect=execute_script),
        elements=Mock(return_value=[object()]),
    )
    view.title = Mock()
    view.search = lambda query: request.param.search(view, query)
    return view


@pytest.fixture(autouse=True)
def fast_wait(monkeypatch):
    def fast_wait_for(func, **kwargs):
        kwargs.update(timeout=1, delay=0.001)
        return wait_for(func, **kwargs)

    monkeypatch.setattr(common, 'wait_for', fast_wait_for, raising=False)


def test_search_refreshes_cached_loading_headers(search_view):
    rows = [{0: False, 'Name': 'target.example.com'}]
    table = SearchTable([((None,), [{0: False}]), ((None, 'Name'), rows)])
    assert table.headers == (None,)
    search_view.table = table

    assert search_view.search('target.example.com') == rows
    search_view.searchbox.search.assert_called_once_with('target.example.com')


def test_search_accepts_completed_empty_results(search_view):
    search_view.responses = iter([[]])
    search_view.table = SearchTable([((None, 'Name'), [])])

    assert search_view.search('missing.example.com') == []
    assert search_view.table.cache_clears == 1


@pytest.mark.parametrize('error', [NoSuchElementException(), StaleElementReferenceException()])
def test_search_waits_through_table_replacement(search_view, error):
    rows = [{'Name': 'target.example.com'}]
    search_view.table = SearchTable([error, (('Name',), error), (('Name',), rows)])

    assert search_view.search('target.example.com') == rows


def test_search_times_out_for_permanently_incomplete_headers(search_view):
    search_view.table = SearchTable([((None,), [{0: False}])])

    with pytest.raises(TimedOutError):
        search_view.search('target.example.com')


def test_search_propagates_unexpected_errors(search_view):
    search_view.table = SearchTable([(('Name',), RuntimeError('unexpected table error'))])

    with pytest.raises(RuntimeError, match='unexpected table error'):
        search_view.search('target.example.com')


def test_search_waits_for_its_response_and_replacement_rows(search_view):
    old_rows = [{'Name': 'previous.example.com'}]
    rows = [{'Name': 'target.example.com'}]
    search_view.responses = iter([None, None, ['target.example.com']])
    search_view.table = SearchTable(
        [(('Name',), old_rows), (('Name',), rows)], initial=(('Name',), old_rows)
    )

    assert search_view.search('target.example.com') == rows


def test_search_waits_for_all_expected_rows(search_view):
    rows = [{'Name': 'one.example.com'}, {'Name': 'two.example.com'}]
    search_view.responses = iter([['one.example.com', 'two.example.com']])
    search_view.table = SearchTable(
        [(('Name',), []), (('Name',), rows[:1]), (('Name',), [{0: False}]), (('Name',), rows)],
        initial=(('Name',), []),
    )

    assert search_view.search('name ~ example.com') == rows


def test_search_retries_key_error_while_reading_rows(search_view):
    rows = [{'Name': 'target.example.com'}]
    search_view.table = SearchTable(
        [(('Name',), KeyError('Name')), (('Name',), rows)],
        initial=(('Name',), KeyError('Name')),
    )

    assert search_view.search('target.example.com') == rows


def test_search_does_not_return_empty_without_completed_empty_state(search_view):
    search_view.responses = iter([[]])
    search_view.table = SearchTable([(('Name',), [])], initial=(('Name',), []))
    search_view.browser.elements.side_effect = [[], [], [object()]]

    assert search_view.search('missing.example.com') == []
    assert search_view.browser.elements.call_count > 1


def test_search_allows_table_to_appear_after_initial_wait(search_view):
    rows = [{'Name': 'target.example.com'}]
    search_view.browser.wait_for_element.return_value = False
    search_view.table = SearchTable([NoSuchElementException(), (('Name',), rows)])

    assert search_view.search('target.example.com') == rows


def test_search_cleans_up_request_tracking_after_failure(search_view):
    search_view.table = SearchTable([(('Name',), RuntimeError('unexpected table error'))])

    with pytest.raises(RuntimeError):
        search_view.search('target.example.com')

    assert search_view.browser.execute_script.call_args.args == (
        'delete window.__airgunHostsSearch;',
    )


def test_search_accepts_display_names_from_response(search_view):
    rows = [{'Name': 'target'}]
    search_view.responses = iter([['target']])
    search_view.table = SearchTable([(('Name',), rows)])

    assert search_view.search('target.example.com') == rows

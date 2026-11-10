from types import SimpleNamespace
from unittest.mock import Mock, call

import pytest
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from wait_for import TimedOutError
from widgetastic.exceptions import RowNotFound

from airgun.entities import host_new


@pytest.fixture
def fast_wait(monkeypatch):
    """Keep real polling behavior without waiting a second between attempts."""
    wait_for = host_new.wait_for

    def fast_wait_for(func, **kwargs):
        kwargs.update(timeout=1, delay=0.001)
        return wait_for(func, **kwargs)

    monkeypatch.setattr(host_new, 'wait_for', fast_wait_for)


def test_host_details_waits_for_headers_and_searched_row(fast_wait):
    """A cached loading-state header must not prevent selecting the eventual host."""
    link = Mock()
    link.click.side_effect = [StaleElementReferenceException('The table was rerendered'), None]

    class LoadingTable:
        def __init__(self):
            self.cached_headers = ()  # Simulate headers cached while loading.
            self.states = iter(('not present', 'loading', 'waiting', 'rerendering', 'ready'))
            self.states_seen = []
            self.state = None

        def clear_cache(self):
            self.cached_headers = None
            self.state = next(self.states)
            self.states_seen.append(self.state)

        @property
        def headers(self):
            if self.state == 'not present':
                raise NoSuchElementException('The table has not appeared yet')
            if self.cached_headers is None:
                self.cached_headers = () if self.state == 'loading' else ('Name',)
            return self.cached_headers

        def row(self, *, Name):
            assert Name == 'target.example.com'
            if self.state == 'waiting':
                raise RowNotFound('The search result has not appeared yet')
            return {'Name': SimpleNamespace(widget=link)}

    table = LoadingTable()
    parent = SimpleNamespace(
        searchbox=SimpleNamespace(search=Mock()),
        browser=SimpleNamespace(plugin=SimpleNamespace(ensure_page_safe=Mock())),
        title=Mock(),
        table=table,
    )

    host_new.ShowNewHostDetails.step(
        SimpleNamespace(parent=parent), entity_name='target.example.com'
    )

    parent.searchbox.search.assert_called_once_with('target.example.com')
    assert table.states_seen == ['not present', 'loading', 'waiting', 'rerendering', 'ready']
    assert link.click.call_args_list == [call(), call()]


def test_host_details_times_out_when_host_never_appears(fast_wait):
    """A missing host must not be mistaken for successful navigation."""
    table = Mock()
    table.headers = ('Name',)
    table.row.side_effect = RowNotFound('No matching host')
    parent = SimpleNamespace(searchbox=Mock(), browser=Mock(), title=Mock(), table=table)

    with pytest.raises(TimedOutError):
        host_new.ShowNewHostDetails.step(
            SimpleNamespace(parent=parent), entity_name='missing.example.com'
        )


@pytest.mark.parametrize(
    'error', [NameError('Unexpected name error'), RuntimeError('Unexpected error')]
)
def test_host_details_does_not_hide_unexpected_errors(fast_wait, error):
    table = Mock()
    table.headers = ('Name',)
    table.row.side_effect = error
    parent = SimpleNamespace(searchbox=Mock(), browser=Mock(), title=Mock(), table=table)

    with pytest.raises(type(error), match=str(error)):
        host_new.ShowNewHostDetails.step(
            SimpleNamespace(parent=parent), entity_name='target.example.com'
        )

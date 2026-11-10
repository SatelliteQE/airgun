from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from selenium.common.exceptions import StaleElementReferenceException
from wait_for import TimedOutError
from widgetastic.exceptions import RowNotFound

from airgun.entities import host_new


@pytest.fixture
def fast_wait(monkeypatch):
    """Keep real polling behavior without waiting a second between attempts."""
    wait_for = host_new.wait_for

    def fast_wait_for(func, **kwargs):
        kwargs.update(timeout=0.1, delay=0.001)
        return wait_for(func, **kwargs)

    monkeypatch.setattr(host_new, 'wait_for', fast_wait_for)


def test_host_details_waits_for_headers_and_searched_row(fast_wait):
    """A cached loading-state header must not prevent selecting the eventual host."""
    link = Mock()

    class LoadingTable:
        def __init__(self):
            self.cached_headers = ()  # The search read the table while loading.
            self.states = iter(('loading', 'waiting', 'rerendering', 'ready'))
            self.states_seen = []

        def clear_cache(self):
            self.cached_headers = None

        def row(self, *, Name):
            assert Name == 'target.example.com'
            state = next(self.states)
            self.states_seen.append(state)
            if self.cached_headers is None:
                self.cached_headers = () if state == 'loading' else ('Name',)
            if 'Name' not in self.cached_headers:
                raise NameError('Could not find column Name')
            if state == 'waiting':
                raise RowNotFound('The search result has not appeared yet')
            if state == 'rerendering':
                raise StaleElementReferenceException('The table was rerendered')
            return {'Name': SimpleNamespace(widget=link)}

    table = LoadingTable()
    parent = SimpleNamespace(search=Mock(), table=table)

    host_new.ShowNewHostDetails.step(
        SimpleNamespace(parent=parent), entity_name='target.example.com'
    )

    parent.search.assert_called_once_with('target.example.com')
    assert table.states_seen == ['loading', 'waiting', 'rerendering', 'ready']
    link.click.assert_called_once_with()


def test_host_details_times_out_when_host_never_appears(fast_wait):
    """A missing host must not be mistaken for successful navigation."""
    table = Mock()
    table.row.side_effect = RowNotFound('No matching host')
    parent = SimpleNamespace(search=Mock(), table=table)

    with pytest.raises(TimedOutError):
        host_new.ShowNewHostDetails.step(
            SimpleNamespace(parent=parent), entity_name='missing.example.com'
        )


def test_host_details_does_not_hide_unexpected_errors(fast_wait):
    table = Mock()
    table.row.side_effect = RuntimeError('Unexpected error')
    parent = SimpleNamespace(search=Mock(), table=table)

    with pytest.raises(RuntimeError, match='Unexpected error'):
        host_new.ShowNewHostDetails.step(
            SimpleNamespace(parent=parent), entity_name='target.example.com'
        )

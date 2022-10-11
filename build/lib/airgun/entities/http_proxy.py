from navmazing import NavigateToSibling

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.utils import retry_navigation
from airgun.views.http_proxy import HTTPProxyCreateView
from airgun.views.http_proxy import HTTPProxyEditView
from airgun.views.http_proxy import HTTPProxyView


class HTTPProxyEntity(BaseEntity):
    endpoint_path = '/http_proxies'

    def create(self, values):
        """Create a new http-proxy."""
        view = self.navigate_to(self, 'New')
        view.http_proxy.disable_pass.click()
        view.fill(values)
        view.submit.click()
        view.validations.assert_no_errors()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def search(self, value):
        """Search for 'value' and return http-proxy names that match.

        :param value: text to filter (default: no filter)
        """
        view = self.navigate_to(self, 'All')
        return view.search(value)

    def read(self, entity_name, widget_names=None):
        """Return dict with properties of http-proxy."""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        return view.read(widget_names=widget_names)

    def update(self, entity_name, values):
        """Update an existing http-proxy."""
        view = self.navigate_to(self, 'Edit', entity_name=entity_name)
        view.http_proxy.disable_pass.click()
        view.fill(values)
        view.submit.click()
        view.validations.assert_no_errors()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def delete(self, entity_name):
        """Delete existing http-proxy entity"""
        view = self.navigate_to(self, 'All')
        self.search(entity_name)
        view.table.row(Name=entity_name)['Actions'].widget.click(handle_alert=True)
        view.validations.assert_no_errors()
        view.flash.assert_no_error()
        view.flash.dismiss()


@navigator.register(HTTPProxyEntity, 'All')
class ShowAllHTTPProxy(NavigateStep):
    """Navigate to All http-proxy page"""

    VIEW = HTTPProxyView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Infrastructure', 'HTTP Proxies')


@navigator.register(HTTPProxyEntity, 'New')
class AddNewHTTPProxy(NavigateStep):
    """Navigate to Create HTTP Proxy page"""

    VIEW = HTTPProxyCreateView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.parent.new.click()


@navigator.register(HTTPProxyEntity, 'Edit')
class EditHTTPProxy(NavigateStep):
    """Navigate to Edit HTTP Proxy page

    Args:
        entity_name: name of the HTTP Proxy
    """

    VIEW = HTTPProxyEditView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(Name=entity_name)['Name'].widget.click()

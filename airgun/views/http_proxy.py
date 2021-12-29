from widgetastic.widget import Table
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SatTab
from airgun.views.common import SearchableViewMixin
from airgun.widgets import MultiSelect
from airgun.widgets import Pf4ConfirmationDialog


class HTTPProxyView(BaseLoggedInView, SearchableViewMixin):
    title = Text('//*[(self::h1 or self::h5) and text()="HTTP Proxies"]')
    new = Text('//a[text()="New HTTP Proxy"]')
    table = Table(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'URL': Text('./a'),
            'Actions': Text(".//a[@data-method='delete']"),
        },
    )
    dialog = Pf4ConfirmationDialog()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class HTTPProxyCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')
    cancel = Text('//a[text()="Cancel"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'HTTP Proxies'
            and self.breadcrumb.read() == 'New HTTP Proxy'
        )

    @View.nested
    class http_proxy(SatTab):
        TAB_NAME = 'HTTP Proxy'
        name = TextInput(id='http_proxy_name')
        url = TextInput(id='http_proxy_url')
        username = TextInput(id='http_proxy_username')
        disable_pass = Text('//a[@id="disable-pass-btn"]')
        password = TextInput(id='http_proxy_password')
        test_url = TextInput(id='http_proxy_test_url')
        test_connection = Text('//a[@id="test_connection_button"]')

    @View.nested
    class locations(SatTab):
        resources = MultiSelect(id='ms-http_proxy_location_ids')

    @View.nested
    class organizations(SatTab):
        resources = MultiSelect(id='ms-http_proxy_organization_ids')


class HTTPProxyEditView(HTTPProxyCreateView):
    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Http Proxies'
            and self.breadcrumb.read().startswith('Edit ')
        )

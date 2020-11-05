from widgetastic.widget import Table
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SatTab
from airgun.views.common import SearchableViewMixin
from airgun.widgets import CustomParameter
from airgun.widgets import FilteredDropdown
from airgun.widgets import MultiSelect


class DomainListView(BaseLoggedInView, SearchableViewMixin):
    """List of all domains."""

    title = Text("//h1[text()='Domains']")
    new = Text("//a[contains(@href, '/domains/new')]")
    table = Table(
        './/table',
        column_widgets={
            'Description': Text("./a"),
            'Hosts': Text("./a"),
            'Actions': Text(".//a[@data-method='delete']"),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class DomainCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit_button = Text(".//input[@name='commit']")
    cancel_button = Text(".//a[@href='/domains']")

    @View.nested
    class domain(SatTab):  # noqa
        dns_domain = TextInput(id='domain_name')
        full_name = TextInput(id='domain_fullname')
        dns_capsule = FilteredDropdown(id='domain_dns_id')

    @View.nested
    class parameters(SatTab):  # noqa
        params = CustomParameter(id='global_parameters_table')

    @View.nested
    class locations(SatTab):  # noqa
        multiselect = MultiSelect(id='ms-domain_location_ids')

    @View.nested
    class organizations(SatTab):  # noqa
        multiselect = MultiSelect(id='ms-domain_organization_ids')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Domains'
            and self.breadcrumb.read() == 'Create Domain'
        )


class DomainEditView(DomainCreateView):
    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Domains'
            and self.breadcrumb.read().startswith('Edit ')
        )

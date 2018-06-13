from widgetastic.widget import Text, TextInput, View

from airgun.views.common import BaseLoggedInView, SearchableViewMixin, SatTab
from airgun.widgets import (
    CustomParameter,
    FilteredDropdown,
    MultiSelect,
    SatTable,
)


class DomainListView(BaseLoggedInView, SearchableViewMixin):
    """List of all domains."""
    # Delete button isn't the typical "btn"
    # It sits within a span, we'll access the href via a Text widget
    table = SatTable(
        locator='table#domains_list',
        column_widgets={
            'Description': Text(".//a[contains(@data-id, '_edit')]"),
            'Hosts': Text(".//a[@data-id='aid_hosts']"),
            'Actions': Text(".//a[@data-method='delete']")  # delete button
        }
    )
    create_button = Text(".//a[@href='/domains/new']")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.table, exception=False) is not None


class DomainCreateView(BaseLoggedInView):
    # Use 'Text' to make submit_button clickable
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
        locator = 'form#new_domain'
        return self.browser.wait_for_element(
            locator, exception=False) is not None


class DomainEditView(DomainCreateView):
    @property
    def is_displayed(self):
        locator = "//form[contains(@id, 'edit_domain_')]"
        return self.browser.wait_for_element(
            locator, exception=False) is not None

from widgetastic.widget import Text, TextInput, View, GenericLocatorWidget
from widgetastic_patternfly import Button

from airgun.views.common import BaseLoggedInView, SearchableViewMixin, SatTab
from airgun.widgets import CustomParameter, FilteredDropdown, MultiSelect, SatTable


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
    create_button = Button(href='/domains/new')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.table, exception=False) is not None


class DomainCreateView(BaseLoggedInView):
    form = GenericLocatorWidget('form#new_domain')

    submit_button = Button(name='commit')
    cancel_button = Button(href='/domains')

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
        return self.browser.wait_for_element(
            self.form, exception=False) is not None


class DomainEditView(DomainCreateView):
    form = GenericLocatorWidget("//form[contains(@id, 'edit_domain_')]")

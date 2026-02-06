from widgetastic.widget import Table, Text, TextInput, View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SatTab, SearchableViewMixinPF4
from airgun.widgets import CustomParameter, FilteredDropdown, MultiSelect


class DomainListView(BaseLoggedInView, SearchableViewMixinPF4):
    """List of all domains."""

    title = Text('//*[(self::h1 or self::h5) and normalize-space(.)="Domains"]')
    new = Text('//a[normalize-space(.)="Create Domain"]')
    table = Table(
        './/table',
        column_widgets={
            'Description': Text('./a'),
            'Hosts': Text('./a'),
            'Actions': Text(".//a[@data-method='delete']"),
        },
    )

    @property
    def is_displayed(self):
        return self.title.is_displayed


class DomainCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit_button = Text(".//input[@name='commit']")
    cancel_button = Text(".//a[@href='/domains']")

    @View.nested
    class domain(SatTab):
        dns_domain = TextInput(id='domain_name')
        full_name = TextInput(id='domain_fullname')
        dns_capsule = FilteredDropdown(id='domain_dns_id')

    @View.nested
    class parameters(SatTab):
        params = CustomParameter(id='global_parameters_table')

    @View.nested
    class locations(SatTab):
        multiselect = MultiSelect(id='ms-domain_location_ids')

    @View.nested
    class organizations(SatTab):
        multiselect = MultiSelect(id='ms-domain_organization_ids')

    @property
    def is_displayed(self):
        return (
            self.breadcrumb.is_displayed
            and self.breadcrumb.locations[0] == 'Domains'
            and self.breadcrumb.read() == 'Create Domain'
        )


class DomainEditView(DomainCreateView):
    @property
    def is_displayed(self):
        return (
            self.breadcrumb.is_displayed
            and self.breadcrumb.locations[0] == 'Domains'
            and self.breadcrumb.read().startswith('Edit ')
        )

from widgetastic.widget import Table, Text, TextInput, View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SearchableViewMixin, SatTab
from airgun.widgets import (
    CustomParameter,
    FilteredDropdown,
    MultiSelect,
    RadioGroup,
)


class SubnetsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Subnets']")
    new = Text("//a[contains(@href, '/subnets/new')]")
    table = Table(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Hosts': Text('./a'),
            'Actions': Text('.//a[@data-method="delete"]'),
        }
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class SubnetCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Subnets'
            and self.breadcrumb.read() == 'Create Subnet'
        )

    @View.nested
    class subnet(SatTab):
        name = TextInput(id='subnet_name')
        description = TextInput(id='subnet_description')
        protocol = RadioGroup(locator="//div[label[contains(., 'Protocol')]]")
        network_address = TextInput(id='subnet_network')
        network_prefix = TextInput(id='subnet_cidr')
        network_mask = TextInput(id='subnet_mask')
        gateway_address = TextInput(id='subnet_gateway')
        primary_dns = TextInput(id='subnet_dns_primary')
        secondary_dns = TextInput(id='subnet_dns_secondary')
        ipam = FilteredDropdown(id='subnet_ipam')
        vlanid = TextInput(id='subnet_vlanid')
        mtu = TextInput(id='subnet_mtu')
        boot_mode = FilteredDropdown(id='subnet_boot_mode')

    @View.nested
    class remote_execution(SatTab):
        TAB_NAME = 'Remote Execution'
        capsules = MultiSelect(id='ms-subnet_remote_execution_proxy_ids')

    @View.nested
    class domains(SatTab):
        resources = MultiSelect(id='ms-subnet_domain_ids')

    @View.nested
    class capsules(SatTab):
        dhcp_capsule = FilteredDropdown(id='subnet_dhcp_id')
        tftp_capsule = FilteredDropdown(id='subnet_tftp_id')
        reverse_dns_capsule = FilteredDropdown(id='subnet_dns_id')
        discovery_capsule = FilteredDropdown(id='subnet_discovery_id')

    @View.nested
    class parameters(SatTab):
        subnet_params = CustomParameter(id='global_parameters_table')

    @View.nested
    class locations(SatTab):
        resources = MultiSelect(id='ms-subnet_location_ids')

    @View.nested
    class organizations(SatTab):
        resources = MultiSelect(id='ms-subnet_organization_ids')


class SubnetEditView(SubnetCreateView):

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Subnets'
            and self.breadcrumb.read().startswith('Edit ')
        )

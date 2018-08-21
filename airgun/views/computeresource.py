from widgetastic.widget import (
    Checkbox,
    Select,
    Text,
    TextInput,
    View,
    ConditionalSwitchableView,
)
from airgun.views.common import (
    BaseLoggedInView,
    SearchableViewMixin,
    SatTab,
)
from airgun.widgets import (
    FilteredDropdown,
    ActionsDropdown,
    SatTable,
    MultiSelect,
)
from widgetastic_patternfly import BreadCrumb


class ComputeResourcesView(BaseLoggedInView, SearchableViewMixin):

    title = Text("//h1[text()='Compute Resources']")
    new = Text("//a[contains(@href, '/compute_resources/new')]")
    table = SatTable(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Actions': ActionsDropdown("./div[contains(@class, 'btn-group')]"),
        }
    )

    @property
    def is_displayed(self):
        """Check if the right page is displayed"""
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class ResourceProviderCreateView(BaseLoggedInView):
    name = TextInput(id='compute_resource_name')
    description = TextInput(id='compute_resource_description')
    submit = Text('//input[@name="commit"]')

    provider = FilteredDropdown(id='s2id_compute_resource_provider')
    provider_content = ConditionalSwitchableView(reference='provider')

    @provider_content.register('Docker')
    class DockerProviderForm(View):
        url = TextInput(id='compute_resource_url')
        user = TextInput(id='compute_resource_user')
        password = TextInput(id='compute_resource_password')
        email = TextInput(id='compute_resource_email')

    @provider_content.register('EC2')
    class EC2ProviderForm(View):
        http_proxy = TextInput(id='compute_resource_http_proxy_id')
        access_key = TextInput(id='compute_resource_user')
        secret_key = TextInput(id='compute_resource_password')
        load_regions = Text("//*[contains(@id,'test_connection_button')]")
        region = FilteredDropdown(id='s2id_compute_resource_region')

        def after_fill(self, was_change):
            self.load_regions.click()

    @provider_content.register('Google')
    class GCEProviderForm(View):
        google_project_id = TextInput(id='compute_resource_project')
        client_email = TextInput(id='compute_resource_email')
        certificate_path = TextInput(id='compute_resource_key_path')
        load_zones = Text("//*[contains(@id,'test_connection_button')]")

    @provider_content.register('Libvirt')
    class LibvirtProviderForm(View):
        url = TextInput(id='compute_resource_url')
        display_type = Select(id='compute_resource_display_type')
        console_passwords = Checkbox(
            id='compute_resource_set_console_password')

    @provider_content.register('RHEL OpenStack Platform')
    class OpenStackProviderForm(View):
        url = TextInput(id='compute_resource_url')
        user = TextInput(id='compute_resource_user')
        password = TextInput(id='compute_resource_password')
        domain = TextInput(id='compute_resource_domain')

    @provider_content.register('Rackspace')
    class RackspaceProviderForm(View):
        url = TextInput(id='compute_resource_url')
        user = TextInput(id='compute_resource_user')
        api_key = TextInput(id='compute_resource_password')
        region = Select(id='compute_resource_region')

    @provider_content.register('VMware')
    class VMwareProviderForm(View):
        vcenter = TextInput(id='compute_resource_server')
        user = TextInput(id='compute_resource_user')
        password = TextInput(id='compute_resource_password')
        display_type = Select(id='compute_resource_display_type')
        vnc_console_passwords = Checkbox(
            id='compute_resource_set_console_password')
        enable_caching = Checkbox(id='compute_resource_caching_enabled')
        load_datacenters = Text("//*[contains(@id,'test_connection_button')]")

        def after_fill(self, was_change):
            self.load_datacenters.click()

    @provider_content.register('RHV')
    class RHVProviderForm(View):
        url = TextInput(id='compute_resource_url')
        user = TextInput(id='compute_resource_user')
        password = TextInput(id='compute_resource_password')
        api4 = Checkbox(id='compute_resource_use_v4')
        certification_authorities = TextInput(id='compute_resource_public_key')

        @View.nested
        class datacenter(View):
            load_datacenters = Text(
                "//a[contains(@id,'test_connection_button')]")
            value = FilteredDropdown(id='s2id_compute_resource_uuid')

            def before_fill(self, values=None):
                self.load_datacenters.click()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None


class ResourceProviderEditView(ResourceProviderCreateView):

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Compute resources'
            and self.breadcrumb.read().startswith('Edit ')
        )


class ResourceProviderDetailView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    flavor = FilteredDropdown(id='s2id_compute_attribute_vm_attrs_flavor_id')
    availability_zone = FilteredDropdown(
        id='s2id_compute_attribute_vm_attrs_availability_zone')
    subnet = FilteredDropdown(id='s2id_compute_attribute_vm_attrs_subnet_id')
    security_groups = MultiSelect(
        id='ms-compute_attribute_vm_attrs_security_group_ids')
    managed_ip = FilteredDropdown(
        id='s2id_compute_attribute_vm_attrs_managed_ip')
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Compute resources'
            and self.breadcrumb.read() != 'Create Compute Resource'
        )

    @View.nested
    class virtual_machines(SatTab):
        TAB_NAME = 'Virtual Machines'

        table = SatTable(
            './/table',
            column_widgets={
                'Name': Text('./a'),
                'Actions': Text('.//a[@data-method="put"]'),
                'Power': Text('.//span[contains(@class,"label")]'),
            }
        )

    @View.nested
    class compute_profiles(SatTab):
        TAB_NAME = 'Compute profiles'
        table = SatTable(
            './/table',
            column_widgets={
                'Compute profile': Text('./a'),
                'VM Attributes': Text('//span[@class="gray"]'),
            }
        )

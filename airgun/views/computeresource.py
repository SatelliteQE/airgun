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
from airgun.widgets import FilteredDropdown, ActionsDropdown, SatTable
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


class ResourceProviderEditView(BaseLoggedInView):
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
        load_datacenters = Text("//*[contains(@id,'test_connection_button')]")
        datacenter = FilteredDropdown(id='s2id_compute_resource_uuid')
        certification_authorities = TextInput(id='compute_resource_public_key')

        # some of the widgets values need to be filled after the main values
        # has been filled. This values will be saved in this dict when
        # before_fill function is invoked, to be later restored in after_fill
        # function.
        _before_fill_backup_values = {}

        def before_fill(self, values):
            # data center should be filled after form fill and load_datacenters
            # click.
            # initialize backup values
            self._before_fill_backup_values = {}
            datacenter = values.get('datacenter')
            if datacenter is not None:
                self._before_fill_backup_values['datacenter'] = datacenter
                del values['datacenter']

        def after_fill(self, was_change):
            self.load_datacenters.click()
            datacenter = self._before_fill_backup_values.get('datacenter')
            if datacenter is not None:
                self.datacenter.fill(datacenter)

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None


class ResourceProviderDetailView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    compprofiles = Text("//a[text()='Compute profiles']")

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Compute resources'
                and self.browser.wait_for_element(
                    self.compprofiles, exception=False) is not None
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

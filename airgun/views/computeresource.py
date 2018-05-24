from widgetastic.widget import (
    Checkbox,
    Select,
    Text,
    TextInput,
    View,
    ConditionalSwitchableView,
)
from airgun.views.common import BaseLoggedInView, SearchableViewMixin
from airgun.widgets import FilteredDropdown, ActionsDropdown, SatTable


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


class ResourceProviderDetailsView(BaseLoggedInView):
    name = TextInput(id='compute_resource_name')
    description = TextInput(id='compute_resource_description')
    api4 = Checkbox(id='compute_resource_use_v4')
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

    @provider_content.register('GCE')
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

    @provider_content.register('OpenStack')
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

    @provider_content.register('oVirt')
    class oVirtProviderForm(View):
        url = TextInput(id='compute_resource_url')
        user = TextInput(id='compute_resource_user')
        password = TextInput(id='compute_resource_password')
        load_datacenters = Text("//*[contains(@id,'test_connection_button')]")
        certification_authorities = TextInput(id='compute_resource_public_key')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None

from widgetastic.widget import Checkbox, Select, Text, TextInput, View
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

    provider_type = FilteredDropdown(id='s2id_compute_resource_provider')
    provider_content = ConditionalSwitchableView(reference='provider_type')

    @provider_content.register('Docker')
    class DockerProviderForm(View):
        name = TextInput(id='compute_resource_name')
        description = TextInput(id='compute_resource_description')
        url = TextInput(id='compute_resource_url')
        user = TextInput(id='compute_resource_user')
        password = TextInput(id='compute_resource_password')
        email = TextInput(id='compute_resource_email')
        submit = Text('//input[@name="commit"]')

    @provider_content.register('Libvirt')
    class LibvirtProviderForm(View):
        name = TextInput(id='compute_resource_name')
        description = TextInput(id='compute_resource_description')
        url = TextInput(id='compute_resource_url')
        display_type = Select(id='compute_resource_display_type')
        console_passwords = Checkbox(id='compute_resource_set_console_password')
        submit = Text('//input[@name="commit"]')

    @provider_content.register('OpenStack')
    class OpenStackProviderForm(View):
        name = TextInput(id='compute_resource_name')
        description = TextInput(id='compute_resource_description')
        url = TextInput(id='compute_resource_url')
        user = TextInput(id='compute_resource_user')
        password = TextInput(id='compute_resource_password')
        domain = TextInput(id='compute_resource_domain')
        submit = Text('//input[@name="commit"]')

    @provider_content.register('VMware')
    class VMwareProviderForm(View):
        name = TextInput(id='compute_resource_name')
        description = TextInput(id='compute_resource_description')
        vcenter = TextInput(id='compute_resource_server')
        user = TextInput(id='compute_resource_user')
        password = TextInput(id='compute_resource_password')
        datacenter = Text("//*[@class='caption']//*[text()='Load Datacenters']")
        display_type = Select(id='compute_resource_display_type')
        vnc_console_passwords = Checkbox(
            id='compute_resource_set_console_password')
        enable_caching = Checkbox(id='compute_resource_caching_enabled')
        submit = Text('//input[@name="commit"]')

    @provider_content.register('oVirt')
    class oVirtProviderForm(View):
        name = TextInput(id='compute_resource_name')
        description = TextInput(id='compute_resource_description')
        url = TextInput(id='compute_resource_url')
        user = TextInput(id='compute_resource_user')
        password = TextInput(id='compute_resource_password')
        datacenter = Text("//*[@class='caption']//*[text()='Load Datacenters']")
        certification_authorities = TextInput(id='compute_resource_public_key')
        submit = Text('//input[@name="commit"]')

    api4 = Checkbox(id='compute_resource_use_v4')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None

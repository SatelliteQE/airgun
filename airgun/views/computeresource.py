from widgetastic.widget import Checkbox, Select, Text, TextInput
from airgun.views.common import BaseLoggedInView, SearchableViewMixin
from airgun.widgets import FilteredDropdown, ActionsDropdown


class ComputeResourcesView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Compute Resources']")
    new = Text("//a[contains(@href, '/compute_resources/new')]")
    edit = Text(".//span[contains(@class, 'btn')][a/text()='Edit']")
    action_list = ActionsDropdown("//td/div[contains(@class, 'btn-group')]")

    @property
    def is_displayed(self):
        """Check if the right page is displayed"""
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class ResourceProviderDetailsView(BaseLoggedInView):
    name = TextInput(id='compute_resource_name')
    provider = FilteredDropdown(id='s2id_compute_resource_provider')
    description = TextInput(id='compute_resource_description')
    url = TextInput(id='compute_resource_url')
    display_type = Select(id='compute_resource_display_type')
    console_passwords = Checkbox(id='compute_resource_set_console_password')
    user = TextInput(id='compute_resource_user')
    password = TextInput(id='compute_resource_password')
    vcenter = TextInput(id='compute_resource_server')
    datacenter = Text("//*[@class='caption']//*[text()='Load Datacenters']")
    vnc_console_passwords = Checkbox(
        id='compute_resource_set_console_password')
    enable_caching = Checkbox(id='compute_resource_caching_enabled')
    certification_authorities = TextInput(id='compute_resource_public_key')
    test_connection = Text('//a[@id="test_connection_button"]')
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None

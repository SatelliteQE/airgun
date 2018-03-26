from widgetastic.widget import Checkbox, Select, Text, TextInput
from airgun.views.common import BaseLoggedInView, SearchableViewMixin
from airgun.widgets import ConfirmationDialog, LCESelector, SelectActionList, FilteredDropdown


class ComputeResourcesView(BaseLoggedInView, SearchableViewMixin):
    """Basic page with Compute Resources title and Create Compute Resource button"""
    title = Text("//h1[text()='Compute Resources']")
    new = Text("//a[contains(@href, '/compute_resources/new')]")
    edit = Text(
        "//a[contains(@href, 'edit') and "
        "contains(@href, 'compute_resources')]"
    )
    #searchbox = Search()

    @property
    def is_displayed(self):
        """Check if the right page is displayed"""
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class ResourceProviderDocker(BaseLoggedInView):
    """Mandatory boxes to create new compute resource, provider is Docker"""
    name = TextInput(id='compute_resource_name')
    provider = FilteredDropdown(id='s2id_compute_resource_provider')
    description = TextInput(id='compute_resource_description')
    url = TextInput(id='compute_resource_url')
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None

class ResourceProviderLibvirt(BaseLoggedInView):
    """Mandatory boxes to create new compute resource, provider is Libvirt"""
    name = TextInput(id='compute_resource_name')
    provider = FilteredDropdown(id='s2id_compute_resource_provider')
    description = TextInput(id='compute_resource_description')
    url = TextInput(id='compute_resource_url')
    display_type = Select(id='compute_resource_display_type')
    console_passwords = Checkbox(id='compute_resource_set_console_password')
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        """Check if the right page is displayed"""
        return self.browser.wait_for_element(
            self.name, exception=False) is not None

class ResourceProviderLibvirt(BaseLoggedInView):
    """Mandatory boxes to create new compute resource, provider is Libvirt"""
    name = TextInput(id='compute_resource_name')
    provider = FilteredDropdown(id='s2id_compute_resource_provider')
    description = TextInput(id='compute_resource_description')
    url = TextInput(id='compute_resource_url')
    display_type = Select(id='compute_resource_display_type')
    console_passwords = Checkbox(id='compute_resource_set_console_password')
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        """Check if the right page is displayed"""
        return self.browser.wait_for_element(
            self.name, exception=False) is not None

class ResourceProviderOpenStack(BaseLoggedInView):
    """Mandatory boxes to create new compute resource, provider is Openstack"""
    name = TextInput(id='compute_resource_name')
    provider = FilteredDropdown(id='s2id_compute_resource_provider')
    description = TextInput(id='compute_resource_description')
    url = TextInput(id='compute_resource_url')
    user = TextInput(id='compute_resource_user')
    password = TextInput(id='compute_resource_password')
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        """Check if the right page is displayed"""
        return self.browser.wait_for_element(
            self.name, exception=False) is not None

"""
class ComputeResourcesEditView(BaseLoggedInView):
    return_to_all = Text("//h1[text()='Compute Resources']")
    action_list = SelectActionList()
    dialog = ConfirmationDialog()
    lce = LCESelector()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.return_to_all, exception=False) is not None
"""

from widgetastic.widget import Text, TextInput

from airgun.views.common import BaseLoggedInView, SearchableViewMixin
from airgun.widgets import FilteredDropdown


class SubnetView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Subnets']")
    new = Text("//a[contains(@href, '/subnets/new')]")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class SubnetDetailsView(BaseLoggedInView):
    name = TextInput(id='subnet_name')
    network_address = TextInput(id='subnet_network')
    network_prefix = TextInput(id='subnet_cidr')
    network_mask = TextInput(id='subnet_mask')
    boot_mode = FilteredDropdown(id='subnet_boot_mode')
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None

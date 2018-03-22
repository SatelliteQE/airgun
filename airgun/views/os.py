from widgetastic.widget import GenericLocatorWidget, Text, TextInput, View

from airgun.views.common import BaseLoggedInView, SatTab, SearchableViewMixin
from airgun.widgets import CustomParameter, MultiSelect


class OperatingSystemView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Operating systems']")
    new = Text("//a[contains(@href, '/operatingsystems/new')]")
    delete = GenericLocatorWidget(
        "//span[contains(@class, 'btn')]/a[@data-method='delete']")
    edit = Text(
        "//a[contains(@href, 'edit') and contains(@href, 'operatingsystems')]")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class OperatingSystemDetailsView(BaseLoggedInView):
    name = TextInput(locator=".//input[@id='operatingsystem_name']")
    major = TextInput(locator=".//input[@id='operatingsystem_major']")
    architectures = MultiSelect(id='ms-operatingsystem_architecture_ids')
    submit = Text('//input[@name="commit"]')

    @View.nested
    class ptables(SatTab):
        TAB_NAME = 'Partition Table'
        ptables = MultiSelect(id='ms-operatingsystem_ptable_ids')

        def fill(self, values):
            self.ptables.fill(values)

        def read(self):
            return self.ptables.read()

    @View.nested
    class parameters(SatTab):
        TAB_NAME = 'Parameters'
        params = CustomParameter()

        def fill(self, values):
            self.params.fill(values)

        def read(self):
            return self.params.read()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None

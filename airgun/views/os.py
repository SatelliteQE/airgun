from widgetastic.widget import GenericLocatorWidget, Text, TextInput, View

from airgun.views.common import BaseLoggedInView, SearchableViewMixin
from airgun.widgets import MultiSelect


class OperatingSystemView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Operating systems']")
    new = Text("//a[contains(@href, '/operatingsystems/new')]")
    delete = GenericLocatorWidget(
        "//span[contains(@class, 'btn')]/a[@data-method='delete']")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class OperatingSystemDetailsView(BaseLoggedInView):
    name = TextInput(locator="//input[@id='operatingsystem_name']")
    major = TextInput(locator="//input[@id='operatingsystem_major']")
    submit = Text('//input[@name="commit"]')
    architectures = MultiSelect(id='ms-operatingsystem_architecture_ids')

    @View.nested
    class ptables(View):
        view_tab = Text("//a[@href='#ptable']")
        ptables = MultiSelect(id='ms-operatingsystem_ptable_ids')

        def fill(self, values):
            self.browser.click(self.view_tab)
            self.ptables.fill(values)

        def read(self):
            self.browser.click(self.view_tab)
            return self.ptables.read()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None

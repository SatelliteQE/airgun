
from widgetastic.widget import View, Text, TextInput, GenericLocatorWidget

from airgun.widgets import ResourceList, Search

from .common import BaseLoggedInView


class OperatingSystemView(BaseLoggedInView):
    title = Text("//h1[text()='Operating systems']")
    new = Text("//a[contains(@href, '/operatingsystems/new')]")
    delete = GenericLocatorWidget(
        "//span[contains(@class, 'btn')]/a[@data-method='delete']")
    searchbox = Search()
    search_result_locator = "//a[contains(., '%s')]"

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None

    def search(self, query, expected_result=None):
        self.searchbox.search(query)
        return self.browser.element(
            self.search_result_locator % (expected_result or query)).text


class OperatingSystemDetailsView(BaseLoggedInView):
    name = TextInput(locator="//input[@id='operatingsystem_name']")
    major = TextInput(locator="//input[@id='operatingsystem_major']")
    submit = Text('//input[@name="commit"]')
    architectures = ResourceList(
        parent_entity='OperatingSystem', affected_entity='Architecture')

    @View.nested
    class ptables(View):
        view_tab = Text("//a[@href='#ptable']")
        ptables = ResourceList(
            parent_entity='OperatingSystem', affected_entity='Ptable')

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

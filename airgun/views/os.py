
from widgetastic.widget import View, Text, TextInput

from airgun.widgets import ResourceList, Search


class OperatingSystemView(View):
    title = Text("//h1[text()='Operating systems']")
    new = Text("//a[contains(@href, '/operatingsystems/new')]")
    navigate_locator = "//a[@id='menu_item_operatingsystems']"
    search_element = Search()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class OperatingSystemDetailsView(View):
    name = TextInput(locator="//input[@id='operatingsystem_name']")
    major = TextInput(locator="//input[@id='operatingsystem_major']")
    submit = Text('//input[@name="commit"]')
    arch_element = ResourceList(
        parent_entity='OperatingSystem', affected_entity='Architect')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None

    def submit_data(self):
        self.browser.click(self.submit)

    @View.nested
    class ptable(View):
        view_tab = Text("//a[@href='#ptable']")
        ptable_element = ResourceList(
            parent_entity='OperatingSystem', affected_entity='Ptable')

        def fill(self, values):
            self.browser.click(self.view_tab)
            self.ptable_element.fill(values)

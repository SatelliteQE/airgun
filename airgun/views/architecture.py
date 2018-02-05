from navmazing import NavigateToSibling
from widgetastic.widget import ParametrizedView, View, Text, TextInput

from airgun.navigation import BaseNavigator, menu_click, navigator
from airgun.sat_widgets import ResourceList


class ArchitectureView(View):
    title = Text("//h1[text()='Architectures']")
    new = Text("//a[contains(@href, '/architectures/new')]")
    search = Text("//a[contains(., '{}')]")
    navigate_locator = "//a[@id='menu_item_architectures']"

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class ArchitectureDetailsView(ParametrizedView):
    name = TextInput(locator="//input[@id='architecture_name']")
    submit = Text('//input[@name="commit"]')
    os_element = ResourceList(
        parent_entity='Architect', affected_entity='OperatingSystem')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None

    def fill(self, values):
        if 'name' in values and values['name']:
            self.name.fill(values['name'])
        if 'os_names' in values and values['os_names']:
            self.os_element.manage_resource(values['os_names'])

    def submit_data(self):
        self.browser.click(self.submit)


@navigator.register(ArchitectureView, 'All')
class ShowAllArchitectures(BaseNavigator):
    VIEW = ArchitectureView

    def step(self, *args, **kwargs):
        menu_click(
            ["//a[@id='hosts_menu']", self.view.navigate_locator],
            self.view.browser
        )


@navigator.register(ArchitectureView, 'New')
class AddNewArchitecture(BaseNavigator):
    VIEW = ArchitectureDetailsView

    prerequisite = NavigateToSibling('All')

    def step(self, *args, **kwargs):
        self.view.browser.wait_for_element(
            self.parent.new, ensure_page_safe=True)
        self.parent.browser.click(self.parent.new)

from widgetastic.widget import Text, TextInput

from airgun.widgets import ResourceList, Search

from .common import BaseLoggedInView


class ArchitectureView(BaseLoggedInView):
    title = Text("//h1[text()='Architectures']")
    new = Text("//a[contains(@href, '/architectures/new')]")
    edit = Text("//a[contains(@href, 'edit') and contains(@href, 'arch')]")
    searchbox = Search()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class ArchitectureDetailsView(BaseLoggedInView):
    name = TextInput(locator="//input[@id='architecture_name']")
    submit = Text('//input[@name="commit"]')
    operatingsystems = ResourceList(
        parent_entity='Architect', affected_entity='OperatingSystem')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None

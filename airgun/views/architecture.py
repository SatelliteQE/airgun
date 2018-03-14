from widgetastic.widget import Text, TextInput

from airgun.views.common import BaseLoggedInView, SearchableViewMixin
from airgun.widgets import MultiSelect


class ArchitectureView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Architectures']")
    new = Text("//a[contains(@href, '/architectures/new')]")
    edit = Text("//a[contains(@href, 'edit') and contains(@href, 'arch')]")
    delete = Text("//a[contains(@href, '/architectures/') and "
                  "@data-method='delete']")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class ArchitectureDetailsView(BaseLoggedInView):
    name = TextInput(locator="//input[@id='architecture_name']")
    submit = Text('//input[@name="commit"]')
    operatingsystems = MultiSelect(id='ms-architecture_operatingsystem_ids')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None

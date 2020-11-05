from widgetastic.widget import Table
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView
from airgun.views.common import SearchableViewMixin
from airgun.widgets import MultiSelect


class ArchitecturesView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Architectures']")
    new = Text("//a[contains(@href, '/architectures/new')]")
    table = Table(
        './/table',
        column_widgets={
            'Name': Text('./a'),
            'Actions': Text('.//a[@data-method="delete"]'),
        },
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class ArchitectureDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(locator="//input[@id='architecture_name']")
    submit = Text('//input[@name="commit"]')
    operatingsystems = MultiSelect(id='ms-architecture_operatingsystem_ids')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Architectures'
            and self.breadcrumb.read().startswith('Edit ')
        )


class ArchitectureCreateView(ArchitectureDetailsView):
    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Architectures'
            and self.breadcrumb.read() == 'Create Architecture'
        )

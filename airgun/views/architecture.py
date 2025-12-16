from widgetastic.widget import Table, Text, TextInput
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SearchableViewMixin
from airgun.widgets import MultiSelect


class ArchitecturesView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[normalize-space(.)='Architectures']")
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
        return self.title.is_displayed


class ArchitectureDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(locator="//input[@id='architecture_name']")
    submit = Text('//input[@name="commit"]')
    operatingsystems = MultiSelect(id='ms-architecture_operatingsystem_ids')

    @property
    def is_displayed(self):
        return (
            self.breadcrumb.is_displayed
            and self.breadcrumb.locations[0] == 'Architectures'
            and self.breadcrumb.read().startswith('Edit ')
        )


class ArchitectureCreateView(ArchitectureDetailsView):
    @property
    def is_displayed(self):
        return (
            self.breadcrumb.is_displayed
            and self.breadcrumb.locations[0] == 'Architectures'
            and self.breadcrumb.read() == 'Create Architecture'
        )

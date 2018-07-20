from widgetastic.widget import Text, TextInput, View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SatTab, SearchableViewMixin
from airgun.widgets import (
    CustomParameter,
    FilteredDropdown,
    MultiSelect,
    SatTable,
)


class OperatingSystemsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Operating systems']")
    new = Text("//a[contains(@href, '/operatingsystems/new')]")
    table = SatTable(
        './/table',
        column_widgets={
            'Title': Text('./a'),
            'Actions': Text('.//a[@data-method="delete"]'),
        }
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class OperatingSystemEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    submit = Text('//input[@name="commit"]')

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Operatingsystems'
                and self.breadcrumb.read() == 'Edit Operating System'
        )

    @View.nested
    class operating_system(SatTab):
        TAB_NAME = 'Operating System'
        name = TextInput(locator=".//input[@id='operatingsystem_name']")
        major = TextInput(locator=".//input[@id='operatingsystem_major']")
        minor = TextInput(locator=".//input[@id='operatingsystem_minor']")
        description = TextInput(
            locator=".//input[@id='operatingsystem_description']")
        family = FilteredDropdown(id='operatingsystem_family')
        password_hash = FilteredDropdown(id='operatingsystem_password_hash')
        architectures = MultiSelect(id='ms-operatingsystem_architecture_ids')

    @View.nested
    class partition_table(SatTab):
        TAB_NAME = 'Partition Table'
        resources = MultiSelect(id='ms-operatingsystem_ptable_ids')

    @View.nested
    class installation_media(SatTab):
        TAB_NAME = 'Installation Media'
        resources = MultiSelect(id='ms-operatingsystem_medium_ids')

    @View.nested
    class parameters(SatTab):
        TAB_NAME = 'Parameters'
        os_params = CustomParameter(id='global_parameters_table')


class OperatingSystemCreateView(OperatingSystemEditView):

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Operatingsystems'
            and self.breadcrumb.read() == 'Create Operating System'
        )

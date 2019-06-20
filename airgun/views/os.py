from widgetastic.widget import Table, Text, TextInput, View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SatTab, SearchableViewMixin
from airgun.widgets import (
    CustomParameter,
    FilteredDropdown,
    MultiSelect,
)


class TemplatesList(View):
    """List of templates for specific operating system. It can have dynamic
    number of templates per different OS types

    Example html representation::

        <label ... for="provisioning_template_id">PXELinux template *</label>
        <div...>
            <div class="..." id="s2id_operatingsystem_os_default_templates...">
                <a>
                    <span>Kickstart default PXELinux</span>
        ...
        <label ... for="provisioning_template_id">PXEGrub template *</label>
        <div...>
            <div class="..." id="s2id_operatingsystem_os_default_templates...">
                 <a>
                     <span>Kickstart default PXEGrub2</span>

    """
    SELECT = "//label[@for='provisioning_template_id'][contains(.,'%s')]" \
             "/following-sibling::div/div[contains(@id, 'default_templates')]"
    TITLES = "//label[@for='provisioning_template_id']"

    @property
    def selects(self):
        """Get dictionary of currently assigned templates for OS"""
        selects = {}
        for title in self.browser.elements(
                self.TITLES, check_visibility=True):
            selects[title.text] = FilteredDropdown(
                self, locator=self.SELECT % title.text, logger=self.logger)
        return selects

    def read(self):
        """Return dictionary of strings representing title-value pairs for all
        templates assigned to specific operating system
        """
        result = self.selects
        for title, select_value in result.items():
            result[title] = select_value.read()
        return result

    def fill(self, value):
        """Assign provided value for specific operating system template

        :param value: dictionary with title-value pairs of templates to be
            changed for OS (e.g. {'Provisioning template': 'test_template'})
        """
        result = self.selects
        for title, select_value in value.items():
            result[title].fill(select_value)


class OperatingSystemsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Operating Systems']")
    new = Text("//a[contains(@href, '/operatingsystems/new')]")
    table = Table(
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
            and self.breadcrumb.locations[0] == 'Operating Systems'
            and self.breadcrumb.read().startswith('Edit ')
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
    class templates(SatTab):
        resources = TemplatesList()

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
            and self.breadcrumb.locations[0] == 'Operating Systems'
            and self.breadcrumb.read() == 'Create Operating System'
        )

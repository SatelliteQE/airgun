from widgetastic.widget import (
    Checkbox,
    Text,
    TextInput,
    View,
)

from airgun.views.common import (
    BaseLoggedInView,
    SatTab,
    SearchableViewMixin,
)
from airgun.widgets import (
    ACEEditor,
    ActionsDropdown,
    FilteredDropdown,
    MultiSelect
)


class PartitionTableView(BaseLoggedInView, SearchableViewMixin):

    title = Text("//h1[text()='Partition Tables']")
    new = Text("//a[contains(@href, '/ptables/new')]")
    actions = ActionsDropdown("//td//div[contains(@class, 'btn-group')]")
    edit = Text("//a[contains(@href, 'edit') and contains(@href, 'ptables')]")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class PartitionTableEditView(BaseLoggedInView):
    name = TextInput(locator="//input[@id='ptable_name']")
    default = Checkbox(id='ptable_default')
    snippet = Checkbox(id='ptable_snippet')
    os_family = FilteredDropdown(id='s2id_ptable_os_family')
    template = ACEEditor()
    audit_comment = TextInput(id="ptable_audit_comment")
    submit = Text('//input[@name="commit"]')

    @View.nested
    class locations(SatTab):
        TAB_NAME = 'Locations'
        locations = MultiSelect(id='ms-ptable_location_ids')

        def fill(self, values):
            self.locations.fill(values)

        def read(self):
            return self.locations.read()

    @View.nested
    class organizations(SatTab):
        TAB_NAME = 'Organizations'
        organizations = MultiSelect(id='ms-ptable_organization_ids')

        def fill(self, values):
            self.organizations.fill(values)

        def read(self):
            return self.organizations.read()

    @View.nested
    class help(SatTab):
        TAB_NAME = 'Help'

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.submit, exception=False) is not None

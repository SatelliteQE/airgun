from widgetastic.widget import (
    Checkbox,
    ConditionalSwitchableView,
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
    MultiSelect,
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
    template = ACEEditor()
    audit_comment = TextInput(id="ptable_audit_comment")
    submit = Text('//input[@name="commit"]')

    snippet = Checkbox(locator="//input[@id='ptable_snippet']")
    os_family_selection = ConditionalSwitchableView(reference='snippet')

    @os_family_selection.register(True)
    class SnippetOption(View):
        pass

    @os_family_selection.register(False)
    class OSFamilyOption(View):
        os_family = FilteredDropdown(id='s2id_ptable_os_family')

    @View.nested
    class locations(SatTab):
        locations = MultiSelect(id='ms-ptable_location_ids')

        def fill(self, values):
            self.locations.fill(values)

        def read(self):
            return self.locations.read()

    @View.nested
    class organizations(SatTab):
        organizations = MultiSelect(id='ms-ptable_organization_ids')

        def fill(self, values):
            self.organizations.fill(values)

        def read(self):
            return self.organizations.read()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.submit, exception=False) is not None

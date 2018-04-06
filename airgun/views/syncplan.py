from widgetastic.widget import Select, Text, TextInput, View

from airgun.views.common import (
    AddRemoveResourcesView,
    BaseLoggedInView,
    SatTab,
    SearchableViewMixin,
)
from airgun.widgets import (
    ConfirmationDialog,
    DateTime,
    EditableEntry,
    EditableEntryCheckbox,
    EditableDateTime,
    EditableEntrySelect,
    ReadOnlyEntry,
    SelectActionList,
)


class SyncPlanView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h2[contains(., 'Sync Plans')]")
    new = Text("//button[contains(@href, '/sync_plans/new')]")
    edit = Text(
        "//td/a[contains(@ui-sref, 'sync-plan') and "
        "contains(@href, 'sync_plans')]"
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


class SyncPlanCreateView(BaseLoggedInView):
    name = TextInput(id='name')
    description = TextInput(id='description')
    interval = Select(id='interval')
    date_time = DateTime()
    submit = Text("//button[contains(@ng-click, 'handleSave')]")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.name, exception=False) is not None


class SyncPlanEditView(BaseLoggedInView):
    # fixme: change all return_to_all instances to use Breadcrumb widget
    return_to_all = Text("//a[text()='Sync Plans']")
    action_list = SelectActionList()
    dialog = ConfirmationDialog()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.return_to_all, exception=False) is not None

    @View.nested
    class details(SatTab):
        name = EditableEntry(name='Name')
        description = EditableEntry(name='Description')
        date_time = EditableDateTime(name='Start Date')
        next_sync = ReadOnlyEntry(name='Next Sync')
        enabled = EditableEntryCheckbox(name='Sync Enabled')
        interval = EditableEntrySelect(name='Interval')
        products_count = ReadOnlyEntry(name='Products')

    @View.nested
    class products(SatTab):
        resources = View.nested(AddRemoveResourcesView)

from widgetastic.widget import Select, Table, Text, TextInput, View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import (
    AddRemoveResourcesView,
    BaseLoggedInView,
    SatTab,
    SearchableViewMixin,
)
from airgun.widgets import (
    ActionsDropdown,
    ConfirmationDialog,
    DateTime,
    EditableDateTime,
    EditableEntry,
    EditableEntryCheckbox,
    EditableEntrySelect,
    ReadOnlyEntry,
)


class SyncPlansView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h2[contains(., 'Sync Plans')]")
    new = Text("//button[contains(@href, '/sync_plans/new')]")
    table = Table('.//table', column_widgets={'Name': Text('./a')})

    @property
    def is_displayed(self):
        return self.title.is_displayed


class SyncPlanCreateView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    name = TextInput(id='name')
    description = TextInput(id='description')
    interval = Select(id='interval')
    cron_expression = TextInput(id='cron_expression')
    date_time = DateTime()
    submit = Text("//button[contains(@ng-click, 'handleSave')]")

    @property
    def is_displayed(self):
        return (
            self.breadcrumb.is_displayed
            and self.breadcrumb.locations[0] == 'Sync Plans'
            and self.breadcrumb.read() == 'New Sync Plan'
        )


class SyncPlanEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    actions = ActionsDropdown("//div[contains(@class, 'btn-group')]")
    dialog = ConfirmationDialog()

    @property
    def is_displayed(self):
        return (
            self.breadcrumb.is_displayed
            and self.breadcrumb.locations[0] == 'Sync Plans'
            and self.breadcrumb.read() != 'New Sync Plan'
        )

    @View.nested
    class details(SatTab):
        name = EditableEntry(name='Name')
        description = EditableEntry(name='Description')
        date_time = EditableDateTime(name='Start Date')
        next_sync = ReadOnlyEntry(name='Next Sync')
        recurring_logic = ReadOnlyEntry(name='Recurring Logic')
        enabled = EditableEntryCheckbox(name='Sync Enabled')
        interval = EditableEntrySelect(name='Interval')
        cron_expression = EditableEntry(name='Cron Logic')
        products_count = ReadOnlyEntry(name='Products')

    @View.nested
    class products(SatTab):
        resources = View.nested(AddRemoveResourcesView)

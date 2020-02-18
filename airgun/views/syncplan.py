from widgetastic.widget import Select
from widgetastic.widget import Table
from widgetastic.widget import Text
from widgetastic.widget import TextInput
from widgetastic.widget import View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import AddRemoveResourcesView
from airgun.views.common import BaseLoggedInView
from airgun.views.common import SatTab
from airgun.views.common import SearchableViewMixin
from airgun.widgets import ActionsDropdown
from airgun.widgets import ConfirmationDialog
from airgun.widgets import DateTime
from airgun.widgets import EditableDateTime
from airgun.widgets import EditableEntry
from airgun.widgets import EditableEntryCheckbox
from airgun.widgets import EditableEntrySelect
from airgun.widgets import ReadOnlyEntry


class SyncPlansView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h2[contains(., 'Sync Plans')]")
    new = Text("//button[contains(@href, '/sync_plans/new')]")
    table = Table('.//table', column_widgets={'Name': Text('./a')})

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


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
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Sync Plans'
            and self.breadcrumb.read() == 'New Sync Plan'
        )


class SyncPlanEditView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    actions = ActionsDropdown("//div[contains(@class, 'btn-group')]")
    dialog = ConfirmationDialog()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
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

from wait_for import wait_for
from widgetastic.widget import Table, Text, View
from widgetastic_patternfly import BreadCrumb
from widgetastic_patternfly4 import Pagination as PF4Pagination

from airgun.views.common import BaseLoggedInView, SatTab, SearchableViewMixinPF4
from airgun.widgets import (
    ActionsDropdown,
    PieChart,
    ProgressBar,
    ReadOnlyEntry,
    SatTable,
)


class TaskReadOnlyEntry(ReadOnlyEntry):
    BASE_LOCATOR = (
        "//span[contains(., '{}') and contains(@class, 'list-group-item-heading')]//parent::div"
        "/following-sibling::div/span"
    )


class TaskReadOnlyEntryError(ReadOnlyEntry):
    BASE_LOCATOR = "//span[contains(., '{}')]//parent::div/following-sibling::pre"


class TasksView(BaseLoggedInView, SearchableViewMixinPF4):
    title = Text("//h1[normalize-space(.)='Tasks']")
    focus = ActionsDropdown("//div[./button[@id='tasks-dashboard-time-period-dropdown']]")
    table = SatTable(
        ".//div[@class='tasks-table']//table",
        column_widgets={
            'Action': Text('./a'),
        },
    )
    pagination = PF4Pagination()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None

    @View.nested
    class RunningChart(View):
        ROOT = ".//div[@id='running-tasks-card']"
        name = Text("./h2")
        total = PieChart("./div[@class='card-pf-body']")

    @View.nested
    class PausedChart(View):
        ROOT = ".//div[@id='paused-tasks-card']"
        name = Text("./h2")
        total = PieChart("./div[@class='card-pf-body']")

    @View.nested
    class StoppedChart(View):
        ROOT = ".//div[@id='stopped-tasks-card']"
        name = Text("./h2")
        table = Table(
            locator='.//table',
            column_widgets={
                'Total': Text('./button'),
            },
        )

    @View.nested
    class ScheduledChart(View):
        ROOT = ".//div[@id='scheduled-tasks-card']"
        name = Text("./h2")
        total = Text(".//div[@class='scheduled-data']")


class TaskDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()
    BREADCRUMB_LENGTH = 2

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Tasks'
            and len(self.breadcrumb.locations) == self.BREADCRUMB_LENGTH
        )

    @View.nested
    class task(SatTab):
        name = TaskReadOnlyEntry(name='Name')
        result = TaskReadOnlyEntry(name='Result')
        triggered_by = TaskReadOnlyEntry(name='Triggered by')
        execution_type = TaskReadOnlyEntry(name='Execution type')
        start_at = TaskReadOnlyEntry(name='Start at')
        started_at = TaskReadOnlyEntry(name='Started at')
        ended_at = TaskReadOnlyEntry(name='Ended at')
        start_before = TaskReadOnlyEntry(name='Start before')
        state = Text("//div[contains(@class, 'progress-description')]")
        progressbar = ProgressBar(locator='//div[contains(@class,"progress-bar")]')
        output = TaskReadOnlyEntry(name='Output')
        errors = TaskReadOnlyEntryError(name='Errors')

    def wait_for_result(self, timeout=60, delay=1):
        """Wait for invocation job to finish"""
        wait_for(
            lambda: (
                self.is_displayed
                and self.task.progressbar.is_displayed
                and self.task.result.read() == 'success'
            ),
            timeout=timeout,
            delay=delay,
            logger=self.logger,
        )

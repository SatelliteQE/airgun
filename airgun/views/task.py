from wait_for import wait_for

from widgetastic.widget import Text, View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SearchableViewMixin, SatTab
from airgun.widgets import (
    ProgressBar,
    ReadOnlyEntry,
    SatTable,
    Table,
    ActionsDropdown,
    PieChart,
    Pagination
)


class TaskReadOnlyEntry(ReadOnlyEntry):
    BASE_LOCATOR = (
        "//span[contains(., '{}') and contains(@class, 'param-name')]"
        "/following-sibling::span"
    )


class TasksView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Tasks']")
    focus = ActionsDropdown(
        "//div[./button[@id='tasks-dashboard-time-period-dropdown']]"
    )
    table = SatTable(
        ".//div[@id='tasks-table']/table",
        column_widgets={
            'Action': Text('./a'),
        }
    )
    pagination = Pagination()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None

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
            }
        )

    @View.nested
    class ScheduledChart(View):
        ROOT = ".//div[@id='scheduled-tasks-card']"
        name = Text("./h2")
        total = Text(".//div[@class='scheduled-data']")


class TaskDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(
            self.breadcrumb, exception=False)
        return (
                breadcrumb_loaded
                and self.breadcrumb.locations[0] == 'Tasks'
                and len(self.breadcrumb.locations) == 2
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
        progressbar = ProgressBar()
        output = TaskReadOnlyEntry(name='Output')
        errors = TaskReadOnlyEntry(name='Errors')

    def wait_for_result(self, timeout=60, delay=1):
        """Wait for invocation job to finish"""
        wait_for(
            lambda: (self.is_displayed and self.task.progressbar.is_displayed
                     and self.task.result.read() == 'success'
                     and ('0 fail' in self.task.output.read())
                     and self.task.state.read() == 'State: stopped'),
            timeout=timeout,
            delay=delay,
            logger=self.logger,
        )

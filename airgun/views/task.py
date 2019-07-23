from widgetastic.widget import Text, View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import BaseLoggedInView, SearchableViewMixin, SatTab
from airgun.widgets import ProgressBar, ReadOnlyEntry, SatTable


class TaskReadOnlyEntry(ReadOnlyEntry):
    BASE_LOCATOR = (
        "//span[contains(., '{}') and contains(@class, 'param-name')]"
        "/following-sibling::span"
    )


class TasksView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h1[text()='Tasks']")
    table = SatTable(
        ".//div[@id='tasks-table']/table",
        column_widgets={
            'Action': Text('./a'),
        }
    )

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(
            self.title, exception=False) is not None


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

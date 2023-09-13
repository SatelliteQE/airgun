from widgetastic.widget import Text, View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import (
    BaseLoggedInView,
    ReadOnlyEntry,
    SatTab,
    SearchableViewMixin,
    TaskDetailsView,
)
from airgun.widgets import SatTable


class ContainerImageTagsView(BaseLoggedInView, SearchableViewMixin):
    title = Text("//h2[contains(., 'Container Image Tags')]")
    table = SatTable('.//table', column_widgets={'Name': Text('./a')})

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None


class ContainerImageTagDetailsView(TaskDetailsView):
    breadcrumb = BreadCrumb()
    BREADCRUMB_LENGTH = 2

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.browser.wait_for_element(self.breadcrumb, exception=False)
        return (
            breadcrumb_loaded
            and self.breadcrumb.locations[0] == 'Container Image Tags'
            and len(self.breadcrumb.locations) >= self.BREADCRUMB_LENGTH
        )

    @View.nested
    class details(SatTab):
        product = ReadOnlyEntry(name='Product')
        repository = ReadOnlyEntry(name='Repository')

    @View.nested
    class lce(SatTab):
        TAB_NAME = 'Lifecycle Environments'
        table = SatTable(
            './/table',
            column_widgets={'Environment': Text('./a'), 'Content View Version': Text('./a')},
        )

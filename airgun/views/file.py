from widgetastic.widget import Text, View
from widgetastic_patternfly import BreadCrumb

from airgun.views.common import (
    BaseLoggedInView,
    ReadOnlyEntry,
    SatTab,
    SatTable,
)
from airgun.widgets import Search


class FilesView(BaseLoggedInView):
    """Main Files view"""

    title = Text("//h1[contains(., 'Files')]")
    table = SatTable('.//table', column_widgets={'Name': Text('./a'), 'Path': Text('./a')})

    search_box = Search()

    def search(self, query):
        self.search_box.search(query)
        return self.table.read()

    @property
    def is_displayed(self):
        return self.title.is_displayed


class FileDetailsView(BaseLoggedInView):
    breadcrumb = BreadCrumb()

    @property
    def is_displayed(self):
        breadcrumb_loaded = self.breadcrumb.is_displayed

        return breadcrumb_loaded and self.breadcrumb.locations[0] == 'Files'

    @View.nested
    class details(SatTab):
        path = ReadOnlyEntry(name='Checksum')
        checksum = ReadOnlyEntry(name='Path')

    @View.nested
    class content_views(SatTab):
        TAB_NAME = 'Content Views'
        cvtable = SatTable(
            './/table',
            column_widgets={
                'Name': Text('./a'),
                'Environment': Text('./a'),
                'Version': Text('./a'),
            },
        )

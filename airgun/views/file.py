from widgetastic.widget import Text, View

from airgun.views.common import (
    BaseLoggedInView,
    ReadOnlyEntry,
    SatTab,
    SatTable,
    SearchableViewMixinPF4,
)


class FilesView(BaseLoggedInView, SearchableViewMixinPF4):
    """Main Files view"""

    title = Text("//h1[normalize-space(.)='Files']")
    table = SatTable(
        ".//table[.//th[normalize-space(.)='Name'] and .//th[normalize-space(.)='Path'] "
        "and .//th[normalize-space(.)='Checksum']]",
        column_widgets={'Name': Text('./a')},
    )

    @property
    def is_displayed(self):
        return self.title.is_displayed


class FileDetailsView(BaseLoggedInView):
    file_name = Text('//h1')

    @property
    def is_displayed(self):
        return self.file_name.is_displayed

    @View.nested
    class details(SatTab):
        path = ReadOnlyEntry(name='Path')
        checksum = ReadOnlyEntry(name='Checksum')

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

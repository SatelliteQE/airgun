from widgetastic.widget import Text, View
from widgetastic_patternfly5 import Tab as PF5Tab

from airgun.views.common import (
    BaseLoggedInView,
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


class FileRepositoryType(Text):
    """Read the repository type from its icon's accessible label."""

    def read(self):
        return self.browser.get_attribute('aria-label', self).removesuffix('_type_icon')


class FileContentTab(PF5Tab):
    """RoutedTabs renders its content in a sibling div rather than a tab panel."""

    ROOT = './/div[@data-ouia-component-id="routed-tabs"]/following-sibling::div[1]'


class FileDetailsView(BaseLoggedInView):
    file_name = Text('.//h1[@data-ouia-component-id="content-details-text"]')
    breadcrumb = Text('.//*[@data-ouia-component-id="content-details-breadcrumb"]')

    @property
    def is_displayed(self):
        return (
            self.file_name.is_displayed
            and self.breadcrumb.is_displayed
            and self.library_repositories.is_displayed
            and self.content_views.is_displayed
        )

    @View.nested
    class details(View):
        # Keep the existing details dictionary although metadata is now above the tabs.
        path = Text('.//dl//dt[.//span[normalize-space(text())="Path"]]/following-sibling::dd[1]')
        checksum = Text(
            './/dl//dt[.//span[normalize-space(text())="Checksum"]]/following-sibling::dd[1]'
        )

    @View.nested
    class library_repositories(FileContentTab):
        TAB_NAME = 'Library repositories'

        table = SatTable(
            './/table[@data-ouia-component-id="content-repositories-table"]',
            column_widgets={
                'Name': Text('./a'),
                'Type': FileRepositoryType('.//*[local-name()="svg" and @aria-label]'),
                'Product': Text('./a'),
            },
        )

    @View.nested
    class content_views(FileContentTab):
        TAB_NAME = 'Content views'

        cvtable = SatTable(
            './/table[@data-ouia-component-id="file-content-view-versions-table"]',
            column_widgets={'Name': Text('./a')},
        )

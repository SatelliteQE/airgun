from widgetastic.widget import Text
from widgetastic_patternfly5 import (
    Menu as PF5Menu,
    Pagination,
)
from widgetastic_patternfly5.ouia import (
    PatternflyTable as PF5OUIATable,
    Text as OUIAText,
    Title as OUIATitle,
)

from airgun.views.common import BaseLoggedInView, SearchableViewMixinPF4


class FlatpakRemotesView(BaseLoggedInView, SearchableViewMixinPF4):
    """View for the Flatpak Remotes page"""

    title = Text("//h1[normalize-space(.)='Flatpak Remotes']")

    table_loading = Text("//h5[normalize-space(.)='Loading']")
    no_results = Text("//h5[normalize-space(.)='No Results']")

    table = PF5OUIATable(
        component_id='flatpak-remotes-table',
        column_widgets={
            'Name': Text('./a[contains(@href, "flatpak_remotes")]'),
            'URL': Text('./a'),
            2: PF5Menu(locator='.//div[contains(@class, "pf-v5-c-menu")]'),
        },
    )
    pagination = Pagination()

    @property
    def is_displayed(self):
        return (
            self.browser.wait_for_element(self.table_loading, exception=False) is None
            and self.browser.wait_for_element(self.table, exception=False) is not None
        )


class FlatpakRemoteDetailsView(BaseLoggedInView, SearchableViewMixinPF4):
    """View for the Flatpak Remote details page"""

    title = OUIATitle('flatpak-remote-title')
    url = OUIAText('url-text-value')
    subtitle = OUIATitle('flatpak-remote-subtitle')
    decription = OUIAText('flatpak-remote-description')

    table = PF5OUIATable(
        component_id='remote-repos-table',
        column_widgets={
            'Name': Text('./a'),
            'ID': Text('./a'),
            'Last mirrored': Text('./a'),
            'Mirror': Text('./a'),
        },
    )
    pagination = Pagination("//div[@class = 'pf-v5-c-pagination pf-m-bottom tfm-pagination']")

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None

from widgetastic.widget import Text
from widgetastic_patternfly5 import (
    Menu as PF5Menu,
    Pagination,
)
from widgetastic_patternfly5.ouia import (
    PatternflyTable as PF5OUIATable,
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
            'Name': Text('./a'),
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

from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import Text, View
from widgetastic_patternfly5 import (
    Button as PF5Button,
    Pagination as PF5Pagination,
    PatternflyTable as PF5Table,
)
from widgetastic_patternfly5.components.tabs import Tab as PF5Tab
from widgetastic_patternfly5.ouia import (
    PatternflyTable as PF5OUIATable,
    Title as PF5OUIATitle,
)

from airgun.views.common import BaseLoggedInView
from airgun.widgets import PF5Search


class ChildManifestRowView(View):
    """View for child manifest rows in expandable table"""

    ROOT = './/tr[contains(@class, "child-manifest-row")]'

    manifest_digest = Text('.//td[@data-label="Manifest digest"]/a')
    type = Text('.//td[@data-label="Type"]')
    product = Text('.//td[@data-label="Product" and @class="pf-v5-c-table__td"]')
    labels_annotations = Text('.//td[@data-label="Labels | Annotations"]')

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.manifest_digest, exception=False) is not None


class ContainerImagesView(BaseLoggedInView):
    """Main Container Images view with tabs for Synced and Booted images"""

    title = PF5OUIATitle('container-images-title')
    help_button = PF5Button(
        locator='.//button[@data-ouia-component-id="container-images-help-button"]'
    )

    @View.nested
    class synced(PF5Tab):
        """Synced tab for container images"""

        TAB_NAME = 'Synced'
        TAB_LOCATOR = ParametrizedLocator(
            './/button[@data-ouia-component-id="container-images-synced-tab"]'
        )

        searchbox = PF5Search()
        table = PF5Table(
            locator='.//table[contains(@data-ouia-component-id, "synced-container-images-table")]',
            # content_view=ChildManifestRowView,
            column_widgets={
                'Tag': Text('.//td[@data-label="Tag"]'),
                'Manifest digest': ChildManifestRowView,
                'Type': Text('.//td[@data-label="Type"]'),
                'Product': Text('.//td[@data-label="Product"]/a'),
                'Labels | Annotations': Text('.//td[@data-label="Labels | Annotations"]'),
            },
        )
        pagination = PF5Pagination(locator='.//div[@id="options-menu-top-pagination"]')

        def search(self, query):
            """Perform search using searchbox on the page and return table contents.

            :param str query: search query to type into search field
            :return: list of dicts representing table rows
            :rtype: list
            """
            self.searchbox.search(query)
            self.browser.plugin.ensure_page_safe(timeout='60s')
            self.table.wait_displayed()
            return self.table.read()

    @View.nested
    class booted(PF5Tab):
        """Booted tab for container images"""

        TAB_NAME = 'Booted'
        TAB_LOCATOR = ParametrizedLocator(
            './/button[@data-ouia-component-id="container-images-booted-tab"]'
        )

        searchbox = PF5Search()
        table = PF5OUIATable(
            component_id='booted-container-images-table',
            column_widgets={
                'Tag': Text('.//td[@data-label="Tag"]'),
                'Manifest digest': Text('.//td[@data-label="Manifest digest"]/a'),
                'Type': Text('.//td[@data-label="Type"]'),
                'Product': Text('.//td[@data-label="Product"]/a'),
                'Labels | Annotations': Text('.//td[@data-label="Labels | Annotations"]'),
            },
        )
        pagination = PF5Pagination(locator='.//div[@id="options-menu-top-pagination"]')

        def search(self, query):
            """Perform search using searchbox on the page and return table contents.

            :param str query: search query to type into search field
            :return: list of dicts representing table rows
            :rtype: list
            """
            self.searchbox.search(query)
            self.browser.plugin.ensure_page_safe(timeout='60s')
            self.table.wait_displayed()
            return self.table.read()

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None

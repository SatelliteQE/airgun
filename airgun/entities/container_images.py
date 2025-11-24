from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.container_images import ContainerImagesView


class ContainerImagesEntity(BaseEntity):
    """Entity for Container Images."""

    endpoint_path = '/labs/container_images'

    def search_synced(self, value):
        """Search for container images in the Synced tab.

        :param str value: search query to type into search field
        :return: list of table rows that match the search query
        :rtype: list
        """
        view = self.navigate_to(self, 'All')
        view.wait_displayed()
        view.synced.click()
        return view.synced.search(value)

    def search_booted(self, value):
        """Search for container images in the Booted tab.

        :param str value: search query to type into search field
        :return: list of table rows that match the search query
        :rtype: list
        """
        view = self.navigate_to(self, 'All')
        view.wait_displayed()
        view.booted.click()
        return view.booted.search(value)

    def read_synced_table(self):
        """Read the table of synced container images.

        :return: list of table rows
        :rtype: list
        """
        view = self.navigate_to(self, 'All')
        view.wait_displayed()
        # Ensure page is safe before interacting with tabs
        view.browser.plugin.ensure_page_safe(timeout='10s')

        # Wait for the tab button to be present
        tab_button_locator = './/button[@data-ouia-component-id="container-images-synced-tab"]'
        wait_for(
            lambda: view.browser.wait_for_element(tab_button_locator, exception=False) is not None,
            timeout=10,
            delay=0.5,
            handle_exception=False,
        )

        # Check if the synced tab is already selected
        tab_button = view.browser.element(tab_button_locator)
        aria_selected = tab_button.get_attribute('aria-selected')
        class_attr = tab_button.get_attribute('class') or ''
        is_selected = aria_selected == 'true' or 'pf-m-current' in class_attr

        # Only click if the tab is not already selected
        if not is_selected:
            # Use browser click directly to avoid PF5Tab's automatic click mechanism
            view.browser.click(tab_button_locator)
            # Wait for the tab to be selected and table to be ready
            wait_for(
                lambda: (
                    view.browser.element(tab_button_locator).get_attribute('aria-selected')
                    == 'true'
                    and view.browser.wait_for_element(
                        './/table[contains(@data-ouia-component-id, "synced-container-images-table")]',
                        exception=False,
                    )
                    is not None
                ),
                timeout=15,
                delay=0.5,
                handle_exception=False,
            )
        else:
            # Tab is already selected, just wait for the table
            wait_for(
                lambda: view.browser.wait_for_element(
                    './/table[contains(@data-ouia-component-id, "synced-container-images-table")]',
                    exception=False,
                )
                is not None,
                timeout=10,
                delay=0.5,
                handle_exception=False,
            )

        # Ensure page is safe before reading the table
        view.browser.plugin.ensure_page_safe(timeout='5s')

        # Use the existing table from the view which has pagination configured
        # Access it directly to avoid triggering tab click
        synced_tab = view.synced
        table = synced_tab.table
        table.wait_displayed()

        # Read rows using the rows() iterator to avoid issues with reading non-existent rows
        # The table.read() method might try to access rows by index (e.g., tr[19]),
        # which can fail if the table has fewer rows than expected
        # Using rows() iterator ensures we only read rows that actually exist
        return [row.read() for row in table.rows()]

    def read_booted_table(self):
        """Read the table of booted container images.

        :return: list of table rows
        :rtype: list
        """
        view = self.navigate_to(self, 'All')
        view.wait_displayed()
        view.booted.click()
        return view.booted.table.read()

    def expand_row(self, tag_name, tab='synced'):
        """Expand a row in the container images table to view child manifests.

        :param str tag_name: name of the tag to expand
        :param str tab: which tab to use ('synced' or 'booted'), default 'synced'
        :return: list of child manifest rows
        :rtype: list
        """
        view = self.navigate_to(self, 'All')
        view.wait_displayed()
        if tab == 'synced':
            view.synced.click()
            table = view.synced.table
        else:
            view.booted.click()
            table = view.booted.table

        row = table.row(tag=tag_name)
        if hasattr(row, 'expand'):
            row.expand()
        elif hasattr(row, 'click'):
            row.click()
        return table.read()

    def read(self, widget_names=None, tab='synced'):
        """Read all values for widgets in the view.

        :param list widget_names: list of widgets to read
        :param str tab: which tab to read ('synced' or 'booted'), default 'synced'
        :return: dict of widget names and their values
        :rtype: dict
        """
        view = self.navigate_to(self, 'All')
        view.wait_displayed()
        if tab == 'synced':
            view.synced.click()
            return view.synced.read(widget_names=widget_names)
        else:
            view.booted.click()
            return view.booted.read(widget_names=widget_names)


@navigator.register(ContainerImagesEntity, 'All')
class ShowAllContainerImages(NavigateStep):
    """Navigate to All Container Images page."""

    VIEW = ContainerImagesView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Lab Features', 'Container Images')

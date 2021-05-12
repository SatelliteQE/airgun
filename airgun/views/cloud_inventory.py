from selenium.common.exceptions import NoSuchElementException
from wait_for import wait_for
from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import Text
from widgetastic.widget import View
from widgetastic_patternfly import Button
from widgetastic_patternfly import Tab
from widgetastic_patternfly4.switch import Switch

from airgun.exceptions import ReadOnlyWidgetError
from airgun.views.common import BaseLoggedInView
from airgun.widgets import Accordion


class InventoryTab(Tab):
    """Cloud Inventory Upload Tab element.

    This is lightweight subclass needed because Cloud Inventory Upload
    tabs contain icons, and widgetastic_patternfly Tab looks for exact match.
    """

    TAB_LOCATOR = ParametrizedLocator(
        './/ul[contains(@class, "nav-tabs")]/'
        'li[./a[contains(normalize-space(.), {@tab_name|quote})]]'
    )

    def child_widget_accessed(self, widget):
        super().child_widget_accessed(widget)
        wait_for(lambda: widget.parent.is_displayed, timeout=5, delay=1, logger=widget.logger)


class InventoryItemsView(Accordion):
    """Item related to one organization on Cloud Inventory Upload page."""

    ROOT = ParametrizedLocator(".//dl[contains(@class, 'pf-c-accordion account-list')]")
    DESCRIPTION_LOCATOR = (
        './/span[contains(@class, "pf-c-label pf-m-blue pf-m-outline account-icon")]'
    )
    STATUS_ELEMENTS = (
        './/div[contains(@class, "status")][contains(@class, "container")]'
        '/div[contains(@class, "item")]'
    )

    @View.nested
    class generating(InventoryTab):
        process = Text(".//div[contains(@class, 'tab-header')]/div[1]")
        restart = Button('Restart')
        terminal = Text(".//div[@class='terminal']")
        scheduled_run = Text(".//div[contains(@class, 'scheduled_run')]")

    @View.nested
    class uploading(InventoryTab):
        process = Text(".//div[contains(@class, 'tab-header')]/div[1]")
        download_report = Button('contains', 'Download Report')
        terminal = Text(".//div[@class='terminal']")

    @property
    def is_generating(self):
        try:
            self.parent_browser.selenium.find_element_by_xpath(f"{self.STATUS_ELEMENTS}[1]/div")
            return True
        except NoSuchElementException:
            return False

    @property
    def is_uploading(self):
        try:
            self.parent_browser.selenium.find_element_by_xpath(f"{self.STATUS_ELEMENTS}[2]/div")
            return True
        except NoSuchElementException:
            return False

    @property
    def status(self):
        if self.is_generating:
            return "generating"
        if self.is_uploading:
            return "uploading"
        return "idle"

    @property
    def is_active(self):
        classes = self.browser.classes(self)
        return any(['expand-active' in class_ for class_ in classes])

    def child_widget_accessed(self, widget):
        if not self.is_active:
            self.click()

    def read(self):
        return {
            'generating': self.generating.read(),
            'uploading': self.uploading.read(),
            'status': self.status,
            'auto_update': self.parent.parent.auto_update.read(),
            'obfuscate_hostnames': self.parent.parent.obfuscate_hostnames.read(),
            'obfuscate_ips': self.parent.parent.obfuscate_ips.read(),
            'exclude_packages': self.parent.parent.exclude_packages.read(),
        }

    def fill(self, values):
        raise ReadOnlyWidgetError('View is read only, fill is prohibited')


class CloudInventoryListView(BaseLoggedInView):
    """Main RH Cloud Inventory Upload view."""

    title = Text("//h1[@class='inventory_title']")
    auto_update = Switch(".//input[@id='rh-cloud-switcher-allow_auto_inventory_upload']")
    obfuscate_hostnames = Switch(
        ".//input[@id='rh-cloud-switcher-obfuscate_inventory_hostnames-on']"
    )
    obfuscate_ips = Switch(".//input[@id='rh-cloud-switcher-obfuscate_inventory_ips']")
    exclude_packages = Switch(".//input[@id='rh-cloud-switcher-exclude_installed_packages']")

    @View.nested
    class inventory_list(InventoryItemsView):
        """Nested view for the inventory list widgets"""

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None

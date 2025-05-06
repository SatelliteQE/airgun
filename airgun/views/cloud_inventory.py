from selenium.common.exceptions import NoSuchElementException
from wait_for import wait_for
from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import Text, View
from widgetastic_patternfly import Button, Tab
from widgetastic_patternfly4.switch import Switch
from widgetastic_patternfly5 import Button as PF5Button
from widgetastic_patternfly5.ouia import Text as PF5OUIAText

from airgun.exceptions import ReadOnlyWidgetError
from airgun.views.common import BaseLoggedInView
from airgun.widgets import Accordion


class InventoryTab(Tab):
    """Insights Inventory Upload Tab element.

    This is lightweight subclass needed because Insights Inventory Upload
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
    """Item related to one organization on Insights Inventory Upload page."""

    ROOT = './/dl[contains(@class, "pf-v5-c-accordion account-list")]'
    DESCRIPTION_LOCATOR = (
        './/span[contains(@class, "pf-v5-c-label pf-m-blue pf-m-outline account-icon")]'
    )
    STATUS_ELEMENTS = './/div[contains(@class, "status")]/div[contains(@class, "item")]'

    @View.nested
    class generating(InventoryTab):
        process = Text('.//div[contains(@class, "tab-header")]/div[1]')
        restart = Button('contains', 'Generate')
        terminal = Text(
            './/div[contains(@class, "report-generate")]//div[contains(@class, "terminal")]'
        )
        scheduled_run = Text('.//div[contains(@class, "scheduled_run")]')

    @View.nested
    class uploading(InventoryTab):
        process = Text('.//div[contains(@class, "tab-header")]/div[1]')
        download_report = Button('Download Report')
        terminal = Text(
            './/div[contains(@class, "report-upload")]//div[contains(@class, "terminal")]'
        )

    @property
    def is_generating(self):
        try:
            self.parent_browser.element(f'{self.STATUS_ELEMENTS}[1]')
            return True
        except NoSuchElementException:
            return False

    @property
    def is_uploading(self):
        try:
            self.parent_browser.element(f'{self.STATUS_ELEMENTS}[2]')
            return True
        except NoSuchElementException:
            return False

    @property
    def status(self):
        if self.is_generating:
            return 'generating'
        if self.is_uploading:
            return 'uploading'
        return 'idle'

    @property
    def is_active(self):
        classes = self.browser.classes(self)
        return any('expand-active' in class_ for class_ in classes)

    def child_widget_accessed(self, widget):
        if not self.is_active:
            self.click()

    def read(self, widget_names=None):

        final_dict = {
            'generating': self.generating.read(),
            'status': self.status,
            'obfuscate_hostnames': self.parent.obfuscate_hostnames.read(),
            'obfuscate_ips': self.parent.obfuscate_ips.read(),
            'exclude_packages': self.parent.exclude_packages.read(),
        }
        if self.uploading.is_displayed:
            final_dict['uploading'] = self.uploading.read()
        if self.parent.auto_update.is_displayed:
            final_dict['auto_update'] = self.parent.auto_update.read()
        return final_dict

    def fill(self, values):
        raise ReadOnlyWidgetError('View is read only, fill is prohibited')


class CloudInventoryListView(BaseLoggedInView):
    """Main Insights Inventory Upload view."""

    title = Text('//h1[normalize-space(.)="Red Hat Inventory"]')
    auto_update = Switch('.//label[@for="rh-cloud-switcher-allow_auto_inventory_upload"]')
    obfuscate_hostnames = Switch('.//label[@for="rh-cloud-switcher-obfuscate_inventory_hostnames"]')
    obfuscate_ips = Switch('.//label[@for="rh-cloud-switcher-obfuscate_inventory_ips"]')
    exclude_packages = Switch('.//label[@for="rh-cloud-switcher-exclude_installed_packages"]')
    auto_mismatch_deletion = Switch(
        './/label[@for="rh-cloud-switcher-allow_auto_insights_mismatch_delete"]'
    )

    auto_upload_desc = PF5OUIAText('OUIA-Generated-Text-6')
    manual_upload_desc = PF5OUIAText('OUIA-Generated-Text-7')

    cloud_connector = PF5Button(locator='//button[normalize-space(.)="Configure cloud connector"]')
    reconfigure_cloud_connector = PF5Button(
        locator='//button[normalize-space(.)="Reconfigure cloud connector"]'
    )
    sync_status = PF5Button(locator='//button[normalize-space(.)="Sync all inventory status"]')
    inventory_list = View.nested(InventoryItemsView)

    @property
    def is_displayed(self):
        return self.browser.wait_for_element(self.title, exception=False) is not None

    def read(self, widget_names=None):
        return {
            'title': self.title.text,
            'auto_update': self.auto_update.read(),
            'obfuscate_hostnames': self.obfuscate_hostnames.read(),
            'obfuscate_ips': self.obfuscate_ips.read(),
            'exclude_packages': self.exclude_packages.read(),
            'auto_mismatch_deletion': self.auto_mismatch_deletion.read(),
        }

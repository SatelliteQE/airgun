from wait_for import wait_for
from widgetastic.utils import ParametrizedLocator
from widgetastic.widget import Text, View
from widgetastic_patternfly import Tab
from widgetastic_patternfly4.switch import Switch
from widgetastic_patternfly5 import Button as PF5Button, Menu
from widgetastic_patternfly5.ouia import Text as PF5OUIAText

from airgun.exceptions import ReadOnlyWidgetError
from airgun.views.common import BaseLoggedInView
from airgun.widgets import Accordion, Pf5ConfirmationDialog


class DataCollectionMenu(Menu):
    """ """

    IS_ALWAYS_OPEN = False
    BUTTON_LOCATOR = ".//button[contains(@class, '-c-menu-toggle')]"
    ROOT = f'{BUTTON_LOCATOR}/..'


class InventoryTab(Tab):
    """Red Hat Lightspeed Inventory Upload Tab element.

    This is lightweight subclass needed because Red Hat Lightspeed Inventory Upload
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
    """Item related to one organization on Red Hat Lightspeed Inventory Upload page."""

    ROOT = './/dl[contains(@class, "pf-v5-c-accordion account-list")]'
    DESCRIPTION_LOCATOR = (
        './/span[contains(@class, "pf-v5-c-label pf-m-blue pf-m-outline account-icon")]'
    )

    # Task action buttons
    generate_and_upload = PF5Button('Generate and upload report')
    generate_report = PF5Button('Generate report')
    download_report = PF5Button('Download report')

    task_status = Text(locator='.//div[contains(@class, "pf-v5-c-progress__description")]')
    report_saved_to = Text(
        locator=(
            './/dt[.//span[contains(text(), "Report saved to")]]/following-sibling::dd[1]'
            '//div[contains(@class, "pf-v5-c-description-list__text")]'
        )
    )

    @property
    def is_active(self):
        """Check if this accordion item is expanded."""
        classes = self.browser.classes(self)
        return any('expand-active' in class_ for class_ in classes)

    def child_widget_accessed(self, widget):
        """Automatically expand the accordion when accessing child widgets."""
        if not self.is_active:
            self.click()

    def read(self, widget_names=None):
        """Read the current state of the view including all settings."""
        result = {
            'generate_and_upload_displayed': self.generate_and_upload.is_displayed,
            'generate_report_displayed': self.generate_report.is_displayed,
            'download_report_displayed': self.download_report.is_displayed,
            'obfuscate_hostnames': self.parent.obfuscate_hostnames.read(),
            'obfuscate_ips': self.parent.obfuscate_ips.read(),
            'exclude_packages': self.parent.exclude_packages.read(),
        }

        # Include auto_update if it's displayed
        if self.parent.auto_update.is_displayed:
            result['auto_update'] = self.parent.auto_update.read()

        if self.report_saved_to.is_displayed:
            result['report_saved_to'] = self.report_saved_to.read()
            result['task_status'] = self.task_status.read()

        return result

    def fill(self, values):
        """This view is read-only."""
        raise ReadOnlyWidgetError('View is read only, fill is prohibited')


class CloudInventoryListView(BaseLoggedInView):
    """Main Red Hat Lightspeed Inventory Upload view."""

    title = Text('//h1[normalize-space(.)="Red Hat Inventory"]')
    auto_update = Switch('.//label[@for="rh-cloud-switcher-allow_auto_inventory_upload"]')
    data_collection = DataCollectionMenu()
    obfuscate_hostnames = Switch('.//label[@for="rh-cloud-switcher-obfuscate_inventory_hostnames"]')
    obfuscate_ips = Switch('.//label[@for="rh-cloud-switcher-obfuscate_inventory_ips"]')
    exclude_packages = Switch('.//label[@for="rh-cloud-switcher-exclude_installed_packages"]')
    auto_mismatch_deletion = Switch(
        './/label[@for="rh-cloud-switcher-allow_auto_insights_mismatch_delete"]'
    )

    auto_upload_desc = PF5OUIAText('text-enable-report')
    manual_upload_desc = PF5OUIAText('text-restart-button')
    dialog = Pf5ConfirmationDialog()
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
        final_dict = {
            'title': self.title.text,
            'obfuscate_hostnames': self.obfuscate_hostnames.read(),
            'obfuscate_ips': self.obfuscate_ips.read(),
            'exclude_packages': self.exclude_packages.read(),
            'auto_mismatch_deletion': self.auto_mismatch_deletion.read(),
        }
        if self.auto_update.is_displayed:
            final_dict['auto_update'] = self.auto_update.read()

        return final_dict

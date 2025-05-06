from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.cloud_inventory import CloudInventoryListView


class CloudInventoryEntity(BaseEntity):
    endpoint_path = '/foreman_rh_cloud/inventory_upload'

    def read(self, entity_name=None, widget_names=None):
        view = self.navigate_to(self, 'All')
        result = view.read(widget_names=widget_names)
        if entity_name:
            view.inventory_list.toggle(entity_name)
            result.update(view.inventory_list.read())
        return result

    def read_org(self, org_name):
        """Read organization details from the inventory list."""
        view = self.navigate_to(self, 'All')
        view.inventory_list.toggle(org_name)
        result = view.inventory_list.read()
        return result

    def get_displayed_settings_options(self):
        """Get displayed settings options on Red Hat Inventory page"""
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        result = {
            'auto_update': view.auto_update.is_displayed,
            'obfuscate_hostnames': view.obfuscate_hostnames.is_displayed,
            'obfuscate_ips': view.obfuscate_ips.is_displayed,
            'exclude_packages': view.exclude_packages.is_displayed,
            'auto_mismatch_deletion': view.auto_mismatch_deletion.is_displayed,
        }
        return result

    def get_displayed_buttons(self):
        """Get displayed buttons on Red Hat Inventory page"""
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        result = {
            'cloud_connector': view.cloud_connector.is_displayed,
            'reconfigure_cloud_connector': view.reconfigure_cloud_connector.is_displayed,
            'sync_status': view.sync_status.is_displayed,
        }
        return result

    def get_displayed_descriptions(self):
        """Get displayed descriptions on Red Hat Inventory page"""
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        result = {
            'auto_upload_desc': view.auto_upload_desc.is_displayed,
            'manual_upload_desc': view.manual_upload_desc.is_displayed,
        }
        return result

    def get_displayed_inventory_tabs(self):
        """Get displayed inventory tabs on Red Hat Inventory page"""
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        result = {
            'generating': view.inventory_list.generating.is_displayed,
            'uploading': view.inventory_list.uploading.is_displayed,
        }
        return result

    def configure_cloud_connector(self):
        """Configure Cloud Connector"""
        view = self.navigate_to(self, 'All')
        view.cloud_connector.click()
        view.dialog.confirm_dialog.click()

    def is_cloud_connector_configured(self):
        """Check if Cloud Connector is configured"""
        view = self.navigate_to(self, 'All')
        return view.reconfigure_cloud_connector.is_displayed

    def sync_inventory_status(self):
        """Sync Inventory status"""
        view = self.navigate_to(self, 'All')
        view.sync_status.click()

    def generate_report(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.inventory_list.toggle(entity_name)
        view.browser.click(view.inventory_list.generating.restart, ignore_ajax=True)

    def download_report(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.inventory_list.toggle(entity_name)
        view.browser.click(view.inventory_list.uploading.download_report, ignore_ajax=True)
        return self.browser.save_downloaded_file()

    def update(self, values):
        """Update Inventory Upload view."""
        view = self.navigate_to(self, 'All')
        view.fill(values)


@navigator.register(CloudInventoryEntity, 'All')
class ShowCloudInventoryListView(NavigateStep):
    """Navigate to main Inventory Upload page"""

    VIEW = CloudInventoryListView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Insights', 'Inventory Upload')

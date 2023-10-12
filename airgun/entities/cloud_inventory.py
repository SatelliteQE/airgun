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
        self.view.menu.select('Configure', 'RH Cloud', 'Inventory Upload')

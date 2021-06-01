from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
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
        wait_for(
            lambda: view.cloud_connector_status.is_displayed is True,
            handle_exception=True,
            timeout=20,
            delay=1,
            logger=view.logger,
        )
        wait_for(
            lambda: view.cloud_connector_status.is_displayed is False,
            handle_exception=True,
            timeout=180,
            delay=1,
            logger=view.logger,
        )

    def sync_inventory_status(self):
        """Sync Inventory status"""
        view = self.navigate_to(self, 'All')
        view.sync_status.click()
        wait_for(
            lambda: view.sync_status_disabled.is_displayed is True,
            handle_exception=True,
            timeout=20,
            delay=1,
            logger=view.logger,
        )
        wait_for(
            lambda: view.sync_status.is_displayed is True,
            handle_exception=True,
            timeout=20,
            delay=1,
            logger=view.logger,
        )

    def generate_report(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.inventory_list.toggle(entity_name)
        view.browser.click(view.inventory_list.generating.restart, ignore_ajax=True)
        wait_for(
            lambda: view.inventory_list.status == 'generating',
            handle_exception=True,
            timeout=20,
            delay=1,
            logger=view.logger,
        )
        wait_for(
            lambda: view.inventory_list.status == 'idle',
            handle_exception=True,
            timeout=180,
            delay=1,
            logger=view.logger,
        )

    def download_report(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.inventory_list.toggle(entity_name)
        view.browser.click(view.inventory_list.uploading.download_report, ignore_ajax=True)
        wait_for(
            lambda: view.inventory_list.status == 'idle',
            handle_exception=True,
            timeout=180,
            delay=1,
            logger=view.logger,
        )
        return self.browser.save_downloaded_file()

    def update(self, values):
        """Update Inventory Upload view."""
        view = self.navigate_to(self, 'All')
        view.fill(values)


@navigator.register(CloudInventoryEntity, 'All')
class ShowCloudInventoryListView(NavigateStep):
    """Navigate to main Inventory Upload page"""

    VIEW = CloudInventoryListView

    def step(self, *args, **kwargs):
        self.view.menu.select('Configure', 'Inventory Upload')

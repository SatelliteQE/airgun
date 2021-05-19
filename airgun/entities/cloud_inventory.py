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

    def generate_report(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.inventory_list.toggle(entity_name)
        view.browser.click(view.inventory_list.generating.restart, ignore_ajax=True)
        wait_for(
            lambda: view.inventory_list.status == 'idle', timeout=180, delay=1, logger=view.logger
        )

    def download_report(self, entity_name):
        view = self.navigate_to(self, 'All')
        view.inventory_list.toggle(entity_name)
        view.browser.click(view.inventory_list.uploading.download_report, ignore_ajax=True)
        wait_for(
            lambda: view.inventory_list.status == 'idle', timeout=180, delay=1, logger=view.logger
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

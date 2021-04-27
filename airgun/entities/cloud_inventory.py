from wait_for import wait_for

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep
from airgun.navigation import navigator
from airgun.views.cloud_inventory import CloudInventoryListView


class CloudInventoryEntity(BaseEntity):
    endpoint_path = '/foreman_rh_cloud/inventory_upload'

    def read(self, entity_name=None, widget_names=None):
        view = self.navigate_to(self, 'All')
        if entity_name:
            entity_item = next(view.inventory_list[entity_name])
            return entity_item.read()
        return view.read(widget_names=widget_names)

    def generate_report(self, entity_name):
        view = self.navigate_to(self, 'All')
        #entity_item = view.inventory_list.expand(entity_name)
        entity_item = next(view.inventory_list[entity_name])
        entity_item.browser.click(entity_item.generating.restart, ignore_ajax=True)
        wait_for(lambda: entity_item.status == 'idle', timeout=180, delay=1, logger=view.logger)

    def download_report(self, entity_name):
        view = self.navigate_to(self, 'All')
        entity_item = next(view.inventory_list[entity_name])
        entity_item.browser.click(entity_item.uploading.download_report, ignore_ajax=True)
        wait_for(lambda: entity_item.status == 'idle', timeout=180, delay=1, logger=view.logger)
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

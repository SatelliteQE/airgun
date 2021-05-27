from time import sleep

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
        # Fix for status icons not changing state immediately after restart
        """
        here's why we used sleep here:
        When we click on restart button then the process of generating and uploading
        a report gets started. There are two icons one for generating tab and other
        for uploading tab. They indicate users whether process of uploading or
        generating report is finished or in progress. So we were using those icon
        to wait till reports are generated and uploaded based on entity_item.status
        can result in uploading, generating and idle state. But the issue is that
        those icon don't change their state immediately after we start report
        generation process(clicking on restart button), which makes automation
        think that the process is finished(idle), which is not correct. That's
        why we have added sleep to wait for icons to change their state(generating
        or uploading). Also the process of generating/uploading reports takes some
        time either way, so I thought we can wait for few seconds.
        """
        sleep(5)
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
        # Fix for status icons not changing state immediately after restart
        sleep(5)
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

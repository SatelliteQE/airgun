from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.all_hosts import (
    AllHostsTableView,
    BulkHostDeleteDialog,
    HostDeleteDialog,
)


class AllHostsEntity(BaseEntity):
    endpoint_path = '/new/hosts'

    def search(self, host_name):
        """Search for specific Host"""
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        return view.search(host_name)

    def delete(self, host_name):
        """Delete host through table dropdown"""
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.table.wait_displayed()
        view.search(host_name)
        view.table[0][2].widget.item_select('Delete')
        delete_modal = HostDeleteDialog(self.browser)
        if delete_modal.is_displayed:
            delete_modal.confirm_delete.click()

    def bulk_delete_all(self):
        """Delete multiple hosts through bulk action dropdown"""
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        view.select_all.fill(True)
        view.bulk_actions.item_select('Delete')
        delete_modal = BulkHostDeleteDialog(self.browser)
        if delete_modal.is_displayed:
            delete_modal.confirm_checkbox.fill(True)
            delete_modal.confirm_delete.click()


@navigator.register(AllHostsEntity, 'All')
class ShowAllHostsScreen(NavigateStep):
    """Navigate to All Hosts screen."""

    VIEW = AllHostsTableView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'All Hosts')

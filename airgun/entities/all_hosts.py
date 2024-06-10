from widgetastic.exceptions import NoSuchElementException

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.all_hosts import (
    AllHostsManageColumnsView,
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

    def read_table(self):
        """Read All Hosts table"""
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        return view.table.read()

    def delete(self, host_name):
        """Delete host through table dropdown"""
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        view.search(host_name)
        view.table[0][2].widget.item_select('Delete')
        delete_modal = HostDeleteDialog(self.browser)
        if delete_modal.is_displayed:
            delete_modal.confirm_delete.click()
        else:
            raise NoSuchElementException("Delete Modal was not displayed.")
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        view.search(host_name)
        return view.no_results

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
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        return view.no_results

    def manage_table_columns(self, values: dict):
        """
        Select which columns should be displayed in the hosts table.

        :param dict values: items of 'column name: value' pairs
            Example: {'IPv4': True, 'Power': False, 'Model': True}
        """
        view = self.navigate_to(self, 'ManageColumns')
        view.fill(values)
        view.submit()

    def get_displayed_table_headers(self):
        """
        Return displayed columns in the hosts table.

        :return list: header names of the hosts table
        """
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        return view.table.headers


@navigator.register(AllHostsEntity, 'All')
class ShowAllHostsScreen(NavigateStep):
    """Navigate to All Hosts screen."""

    VIEW = AllHostsTableView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'All Hosts')


@navigator.register(AllHostsEntity, 'ManageColumns')
class HostsManageColumns(NavigateStep):
    """Navigate to the Manage columns dialog"""

    VIEW = AllHostsManageColumnsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        """Open the Manage columns dialog"""
        self.parent.manage_columns.click()

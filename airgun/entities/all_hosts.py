from widgetastic.exceptions import NoSuchElementException

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.all_hosts import (
    AllHostsManageColumnsView,
    AllHostsTableView,
    BuildManagementDialog,
    BulkHostDeleteDialog,
    HostDeleteDialog,
    ManageCVEModal,
    ManagePackagesModal,
)
from airgun.views.job_invocation import JobInvocationCreateView


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

    def build_management(self, reboot=False, rebuild=False):
        """Build or rebuild hosts through build management popup"""
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        view.select_all.fill(True)
        view.bulk_actions.item_select('Build management')
        build_management_modal = BuildManagementDialog(self.browser)
        if build_management_modal.is_displayed:
            if reboot:
                build_management_modal.reboot_now.fill(True)
            if rebuild:
                build_management_modal.rebuild_provisioning_only.fill(True)
            build_management_modal.confirm.click()
        self.browser.wait_for_element(view.alert_message, exception=False)
        return view.alert_message.read()

    def manage_cve(self, lce=None, cv=None):
        """Bulk reassign Content View Environments through the All Hosts page
        args:
            lce (str): Lifecycle Environment to swap the hosts to.
            cv (str): CV within that LCE to assign the hosts to.
        """
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        view.select_all.fill(True)
        view.bulk_actions_kebab.click()
        self.browser.move_to_element(view.bulk_actions_menu.item_element('Manage content'))
        view.bulk_actions.item_select('Content view environments')
        view = ManageCVEModal(self.browser)
        view.lce_selector.fill({lce: True})
        view.content_source_select.item_select(cv)
        view.save_btn.click()

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

    def manage_packages_helper(self, view, action_type, packages_to_manage):
        """
        Helper function to manage packages for selected hosts.
        Does repetetive action that needs to happen before running the management action.

        args:
            view (ManagePackagesModal): ManagePackagesModal view
            action_type (str): action type to perform (upgrade, install, remove)
            packages_to_manage (list): list of packages to manage
        """
        radio_button = getattr(view.select_action, f"{action_type}_packages_radio")
        radio_button.fill(True)
        for package in packages_to_manage:
            clear_search = getattr(view, f"{action_type}_packages").clear_search
            if clear_search.is_displayed:
                clear_search.click()
            search_input = getattr(view, f"{action_type}_packages").search_input
            search_input.fill(f'name = "{package}"')
            self.browser.wait_for_element(
                getattr(view, f"{action_type}_packages").table[0][0].widget, exception=False
            )
            getattr(view, f"{action_type}_packages").table[0][0].widget.fill(True)

    def manage_packages(
        self,
        host_names=None,
        select_all_hosts=False,
        upgrade_all_packages=False,
        upgrade_packages=False,
        install_packages=False,
        remove_packages=False,
        packages_to_upgrade=None,
        packages_to_install=None,
        packages_to_remove=None,
        manage_by_customized_rex=False,
    ):
        """
        Navigate to Manage Packages for selected hosts and run the management action based on user input.

        args:
            host_names (str or list): str with one host or list of hosts to select
            select_all_hosts (bool): select all hosts flag
            upgrade_all_packages (bool): upgrade all packages flag
            upgrade_packages (bool): upgrade selected packages flag
            install_packages (bool): install selected packages flag
            remove_packages (bool): remove selected packages flag
            packages_to_upgrade (str or list): str with one package or list of packages to upgrade
            packages_to_install (str or list): str with one package or list of packages to install
            packages_to_remove (str or list): str with one package or list of packages to remove
            manage_by_customized_rex (bool): manage by customized rex flag
        """

        # Check validity of user input
        if select_all_hosts and host_names:
            raise ValueError("Cannot select all and specify host names at the same time!")
        if sum([upgrade_packages, install_packages, remove_packages]) != 1:
            raise ValueError(
                "Only one of the options can be selected: upgrade_packages, install_packages, remove_packages!"
            )

        selected_packages_options = sum(
            [
                packages_to_upgrade is not None,
                packages_to_install is not None,
                packages_to_remove is not None,
            ]
        )
        if selected_packages_options != 1 and not upgrade_all_packages:
            raise ValueError(
                "Exactly one of the options must be selected: packages_to_upgrade, packages_to_install, packages_to_remove!"
            )

        # Navigate to All Hosts
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()

        # Select all hosts from the table
        if select_all_hosts:
            view.select_all.fill(True)
        # Select user-specified hosts
        else:
            if not isinstance(host_names, list):
                host_names = [host_names]
            for host_name in host_names:
                view.search(host_name)
                view.table[0][0].widget.fill(True)

        # Open Manage Packages modal
        view.bulk_actions_kebab.click()
        # This is here beacuse there is nested flyout menu which needs to be hovered over first so we can use item_select in the next step
        self.browser.move_to_element(view.bulk_actions_menu.item_element('Manage content'))
        view.bulk_actions.item_select('Packages')

        view = ManagePackagesModal(self.browser)

        packages_to_install = (
            [packages_to_install]
            if not isinstance(packages_to_install, list)
            else packages_to_install
        )
        packages_to_upgrade = (
            [packages_to_upgrade]
            if not isinstance(packages_to_upgrade, list)
            else packages_to_upgrade
        )
        packages_to_remove = (
            [packages_to_remove] if not isinstance(packages_to_remove, list) else packages_to_remove
        )

        # Select management action and handle the option
        # when user wants to specify packages to upgrade or install
        if upgrade_all_packages:
            view.select_action.upgrade_all_packages_radio.fill(True)

        elif upgrade_packages and (not upgrade_all_packages):
            self.manage_packages_helper(view, 'upgrade', packages_to_upgrade)

        elif install_packages:
            self.manage_packages_helper(view, 'install', packages_to_install)

        elif remove_packages:
            self.manage_packages_helper(view, 'remove', packages_to_remove)

        # In this particular case dropdown has slightly different structure that what is defined in widgetastic
        view.review.manage_via_dropdown.ITEMS_LOCATOR = (
            "//ul[contains(@class, 'pf-c-dropdown__menu')]/li"
        )
        view.review.manage_via_dropdown.ITEM_LOCATOR = (
            "//*[contains(@class, 'pf-c-dropdown__menu-item') and normalize-space(.)={}]"
        )
        # Select how to manage packages
        if not manage_by_customized_rex:
            view.review.expander.click()
            view.review.manage_via_dropdown.item_select('via remote execution')
            view.review.finish_package_management_btn.click()
        else:
            # In this case "Run job" page is opened on which user can specify job details
            # Here we just select tu run with prefilled values
            view.review.expander.click()
            view.review.manage_via_dropdown.item_select('via customized remote execution')
            view.review.finish_package_management_btn.click()
            view = JobInvocationCreateView(self.browser)
            view.submit.click()


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

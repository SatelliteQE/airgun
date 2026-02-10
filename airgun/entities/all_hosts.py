from asyncio import wait_for
import contextlib

import anytree
from widgetastic.exceptions import NoSuchElementException
from widgetastic_patternfly5 import DropdownItemDisabled

from airgun.entities.base import BaseEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.all_hosts import (
    AllHostsManageColumnsView,
    AllHostsTableView,
    BuildManagementDialog,
    BulkHostDeleteDialog,
    ChangeHostCollectionsModal,
    ChangeHostsOwnerModal,
    ChangeLocationModal,
    ChangeOrganizationModal,
    ChangePowerStateModal,
    DisassociateHostsModal,
    HostDeleteDialog,
    HostgroupDialog,
    ManageErrataModal,
    ManagePackagesModal,
    ManageRepositorySetsModal,
    ManageSystemPurposeModal,
    ManageTracesModal,
)
from airgun.views.host_new import ManageMultiCVEnvModal
from airgun.views.job_invocation import JobInvocationCreateView


class AllHostsEntity(BaseEntity):
    endpoint_path = '/new/hosts'

    def search(self, host_name):
        """Search for specific Host"""
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        return view.search(host_name)

    def read_filled_searchbox(self):
        """Read filled searchbox"""
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        return view.searchbox.read()

    def read_table(self):
        """Read All Hosts table"""
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        return view.table.read()

    def delete(self, host_name):
        """Delete host through table dropdown"""
        view = self.all_hosts_navigate_and_select_hosts_helper(host_names=host_name)
        view.table[0][2].widget.item_select('Delete')
        delete_modal = HostDeleteDialog(self.browser)
        if delete_modal.is_displayed:
            delete_modal.confirm_delete.click()
        else:
            raise NoSuchElementException('Delete Modal was not displayed.')
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        view.search(host_name)
        return view.no_results

    def bulk_delete_all(self):
        """Delete multiple hosts through bulk action dropdown"""
        view = self.all_hosts_navigate_and_select_hosts_helper(select_all_hosts=True)
        view.bulk_actions_kebab.click()
        view.bulk_actions_menu.item_select('Delete')
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
        view = self.all_hosts_navigate_and_select_hosts_helper(select_all_hosts=True)
        view.bulk_actions_kebab.click()
        view.bulk_actions_menu.item_select('Build management')
        build_management_modal = BuildManagementDialog(self.browser)
        if build_management_modal.is_displayed:
            if reboot:
                build_management_modal.reboot_now.fill(True)
            if rebuild:
                build_management_modal.rebuild_provisioning_only.fill(True)
            build_management_modal.confirm.click()
        self.browser.wait_for_element(view.alert_message, exception=False)
        return view.alert_message.read()

    def change_hostgroup(self, name):
        """Change hostgroup of all hosts to chosen hostgroup"""
        view = self.all_hosts_navigate_and_select_hosts_helper(select_all_hosts=True)
        view.bulk_actions.item_select('Change host group')
        view = HostgroupDialog(self.browser)
        view.hostgroup_dropdown.item_select(name)
        view.save_button.click()

    def manage_cve(self, lce_name=None, cv_name=None):
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
        view.bulk_actions_manage_content_menu.item_select('Content view environments')
        modal = ManageMultiCVEnvModal(self.browser)
        assignment_section = modal.new_assignment_section(lce_name=lce_name)
        assignment_section.lce_selector.wait_displayed(timeout=5)
        assignment_section.lce_selector.click()
        assignment_section.content_source_select.item_select(cv_name)
        modal.save_btn.click()
        wait_for(lambda: not modal.is_displayed, timeout=10)

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
        radio_button = getattr(view.select_action, f'{action_type}_packages_radio')
        radio_button.fill(True)
        for package in packages_to_manage:
            clear_search = getattr(view, f'{action_type}_packages').clear_search
            if clear_search.is_displayed:
                clear_search.click()
            search_input = getattr(view, f'{action_type}_packages').search_input
            search_input.fill(f'name = "{package}"')
            self.browser.wait_for_element(
                getattr(view, f'{action_type}_packages').table[0][0].widget, exception=False
            )
            getattr(view, f'{action_type}_packages').table[0][0].widget.fill(True)

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

        if sum([upgrade_packages, install_packages, remove_packages]) != 1:
            raise ValueError(
                'Only one of the options can be selected: upgrade_packages, install_packages, remove_packages!'
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
                'Exactly one of the options must be selected: packages_to_upgrade, packages_to_install, packages_to_remove!'
            )

        view = self.all_hosts_navigate_and_select_hosts_helper(host_names, select_all_hosts)

        # Open Manage Packages modal
        view.bulk_actions_kebab.click()
        # This is here beacuse there is nested flyout menu which needs to be hovered over first so we can use item_select in the next step
        self.browser.move_to_element(view.bulk_actions_menu.item_element('Manage content'))
        view.bulk_actions_manage_content_menu.item_select('Packages')

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
            "//ul[contains(@class, 'pf-v5-c-dropdown__menu')]/li"
        )
        view.review.manage_via_dropdown.ITEM_LOCATOR = (
            "//*[contains(@class, 'pf-v5-c-dropdown__menu-item') and normalize-space(.)={}]"
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

    def manage_errata_helper(self, view, erratas_to_apply_by_id, individual_search_queries):
        """
        Helper function to manage errata for selected hosts.
        Based on the user input it finds errata by provied ids or by individual search queries.

        args:
            view (ManageErrataModal): ManageErrataModal view
            erratas_to_apply_by_id (list): list of erratas to apply by their ids
            individual_search_queries (list): list of search queries for each errata
        """

        values_to_iterate = None
        search_query_prefix = ''

        if erratas_to_apply_by_id is not None:
            values_to_iterate = erratas_to_apply_by_id
            search_query_prefix = 'errata_id = '

        elif individual_search_queries is not None:
            values_to_iterate = individual_search_queries

        for search_query in values_to_iterate:
            clear_search = view.select_errata.clear_search
            if clear_search.is_displayed:
                clear_search.click()
            view.select_errata.search_input.fill(f'{search_query_prefix}{search_query}')

            self.browser.wait_for_element(view.select_errata.table[0][0].widget, exception=False)
            view.select_errata.table[0][0].widget.fill(True)

    def manage_errata(
        self,
        host_names=None,
        select_all_hosts=False,
        erratas_to_apply_by_id=None,
        individual_search_queries=None,
        manage_by_customized_rex=False,
    ):
        """
        Navigate to Manage Errata for selected hosts and run the management action based on user input.

        args:
            host_names (str or list): str with one host or list of hosts to select
            select_all_hosts (bool): select all hosts flag
            erratas_to_apply_by_id (str or list): str with one errata or list of erratas to apply by their ids
            individual_search_queries (list): list of string of search queries for each errata, use only if not using erratas_to_apply_by_id!
            manage_by_customized_rex (bool): manage by customized rex flag
        """

        # if both erratas_to_apply_by_id and individual_search_queries are specified, raise an error
        if erratas_to_apply_by_id is not None and individual_search_queries is not None:
            raise ValueError(
                'Cannot specify both erratas_to_apply_by_id and individual_search_queries at the same time!'
            )

        # if erratas_to_apply_by_id is specified, make sure it is a list
        if erratas_to_apply_by_id is not None and not isinstance(erratas_to_apply_by_id, list):
            erratas_to_apply_by_id = [erratas_to_apply_by_id]

        view = self.all_hosts_navigate_and_select_hosts_helper(host_names, select_all_hosts)

        # Open Manage Erratas modal
        view.bulk_actions_kebab.click()
        # This is here beacuse there is nested flyout menu which needs to be hovered over first so we can use item_select in the next step
        self.browser.move_to_element(view.bulk_actions_menu.item_element('Manage content'))
        view.bulk_actions_manage_content_menu.item_select('Errata')

        view = ManageErrataModal(self.browser)

        # Select erratas to apply
        self.manage_errata_helper(view, erratas_to_apply_by_id, individual_search_queries)

        # In this particular case dropdown has slightly different structure that what is defined in widgetastic
        view.review.manage_via_dropdown.ITEMS_LOCATOR = (
            "//ul[contains(@class, 'pf-v5-c-dropdown__menu')]/li"
        )
        view.review.manage_via_dropdown.ITEM_LOCATOR = (
            "//*[contains(@class, 'pf-v5-c-dropdown__menu-item') and normalize-space(.)={}]"
        )
        # Select how to manage errata
        if not manage_by_customized_rex:
            view.review.expander.click()
            view.review.manage_via_dropdown.item_select('via remote execution')
            view.review.finish_errata_management_btn.click()
        else:
            # In this case "Run job" page is opened on which user can specify job details
            # Here we just select to run with prefilled values
            view.review.expander.click()
            view.review.manage_via_dropdown.item_select('via customized remote execution')
            view.review.finish_errata_management_btn.click()
            view = JobInvocationCreateView(self.browser)
            self.browser.plugin.ensure_page_safe(timeout='5s')
            wait_for(lambda: view.submit.is_displayed, timeout=10)
            view.submit.click()

    def manage_repository_sets(
        self,
        host_names=None,
        select_all_hosts=False,
        repository_names=None,
        status_to_change='No change',
        individual_search_queries=None,
    ):
        """
        Navigate to Manage repository sets and change the repository status by selection management action

        args:
            host_names (str or list): str with one host or list of hosts to select
            select_all_hosts (bool): select all hosts flag
            repository_names (str or list): str with one repository or list of repositories to change status
            status_to_change (str): str which has status to be changed for one or more repositories, default set to
            'No change'
            individual_search_queries (list): list of string of search queries for each repo
        """

        # if both repository_names and individual_search_queries are specified, raise an error
        if repository_names is not None and individual_search_queries is not None:
            raise ValueError(
                'Cannot specify both repository_names and individual_search_queries at the same time!'
            )

        # if status_to_change is 'No change', then it will not allow to move ahead so raise an exception
        if status_to_change == 'No change':
            raise ValueError(
                'Value of status_to_change should not be "No change", it will not allow to move next page'
            )

        view = self.all_hosts_navigate_and_select_hosts_helper(host_names, select_all_hosts)

        # Open Manage Repository sets modal
        view.bulk_actions_kebab.click()

        self.browser.move_to_element(view.bulk_actions_menu.item_element('Manage content'))
        view.bulk_actions_manage_content_menu.item_select('Repository sets')

        view = ManageRepositorySetsModal(self.browser)

        # select one or more repositories and change status
        self.manage_repository_sets_helper(
            view, repository_names, individual_search_queries, status_to_change
        )

    def manage_repository_sets_helper(
        self, view, repository_names, individual_search_queries, status_to_change
    ):
        """
        Helper function to manage Repository sets for selected hosts.
        Based on the user input it finds repos by names or by individual search queries.

        args:
            view (ManageRepositorySetsModal): ManageRepositorySetsModal view
            repository_names (list): list of repositories to change
            individual_search_queries (list): list of search queries for each repository
            status_to_change (str): str containing status to change for repositories
        """
        search_query = 'name = "{}"'
        clear_search_cross_button = view.select_repository_sets.clear_search

        # List repository_names contains some repo names
        if repository_names is not None:
            all_repositories = repository_names
        # individual_search_queries contain repository name
        elif individual_search_queries is not None:
            all_repositories = individual_search_queries

        for repo in all_repositories:
            if clear_search_cross_button.is_displayed:
                clear_search_cross_button.click()
            view.select_repository_sets.search_input.fill(search_query.format(repo))

            self.browser.plugin.ensure_page_safe(timeout='5s')
            view.wait_displayed()
            # For some reason it is needed to read the widget first, it fails, but enables filling in the next step
            try:
                _ = view.select_repository_sets.table[0]['Status'].widget
            except anytree.resolver.ResolverError:
                contextlib.suppress(Exception)
            view.select_repository_sets.table[0]['Status'].widget.item_select(status_to_change)

        view.next_btn.click()  # Next button from 'Select repository sets'
        view.next_btn.click()  # Next button from 'Review hosts'
        if view.review.number_of_repository_status_changed.text != str(len(repository_names)):
            raise Exception('Repository count not matches')
        view.review.set_content_overrides.click()

    def get_package_and_errata_wizard_review_hosts_text(
        self,
    ):
        """Return the text from both the manage packages and manage errata modals review hosts step"""
        # Navigate to All Hosts
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        view.select_all.fill(True)

        # Get text from Manage Packages -> Review Hosts
        view.bulk_actions_kebab.click()
        self.browser.move_to_element(view.bulk_actions_menu.item_element('Manage content'))
        view.bulk_actions_manage_content_menu.item_select('Packages')

        view = ManagePackagesModal(self.browser)
        view.select_action.upgrade_all_packages_radio.fill(True)
        manage_package_text = view.review_hosts.content_text.read()
        view.cancel_btn.click()

        # Get text from Manage Errata -> Review Hosts
        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        view.select_all.fill(True)

        # Get text from Manage Packages -> Review Hosts
        view.bulk_actions_kebab.click()
        self.browser.move_to_element(view.bulk_actions_menu.item_element('Manage content'))
        view.bulk_actions_manage_content_menu.item_select('Errata')

        view = ManageErrataModal(self.browser)
        view.next_btn.click()
        manage_errata_text = view.review_hosts.content_text.read()
        return [manage_package_text, manage_errata_text]

    def disassociate_hosts(self, host_names=None, select_all_hosts=False):
        """
        Navigate to the Disassociate hosts modal for selected hosts and disassociate them.

        :param host_names: List of host names to disassociate.
        :param select_all_hosts: If True, all hosts will be selected for disassociation.
        """

        view = self.all_hosts_navigate_and_select_hosts_helper(host_names, select_all_hosts)

        view.bulk_actions_kebab.click()
        view.bulk_actions_menu.item_select('Disassociate hosts')

        view = DisassociateHostsModal(self.browser)
        view.confirm_btn.click()

    def change_power_state(self, state, host_names=None, select_all_hosts=False):
        """
        Change power state for selected hosts.

        Opens the Change power state modal and applies the requested power
        state to the selected hosts.

        :param state: Desired power state (for example, "Start", "Stop", "Power Off", "Reboot").
        :param host_names: List of host names whose power state should be changed. If None, uses the current selection.
        :param select_all_hosts: If True, select all hosts before changing their power state.
        """

        view = self.all_hosts_navigate_and_select_hosts_helper(host_names, select_all_hosts)
        view.wait_displayed()
        view.bulk_actions_kebab.click()
        view.bulk_actions_menu.item_select('Change power state')

        view = ChangePowerStateModal(self.browser)
        view.wait_displayed()
        view.select_state.item_select(state)
        view.apply_btn.click()

    def all_hosts_navigate_and_select_hosts_helper(self, host_names=None, select_all_hosts=False):
        """
        Helper function to navigate to All Hosts and select specified hosts or all hosts.
        This function is used to avoid code duplication in methods that require host selection.

        :param host_names: str with one host or list of hosts to select
        :param select_all_hosts: bool, if True, all hosts will be selected

        :raises ValueError: if both or neither select_all_hosts and host_names are specified

        :return: view (AllHostsTableView)
        """

        if select_all_hosts and host_names:
            raise ValueError('Cannot select all and specify host names at the same time!')
        if not select_all_hosts and not host_names:
            raise ValueError('Must specify either host_names or select_all_hosts.')

        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()

        # This step ensures deterministic state of the table
        # If 'Select none (0)' is disabled, it means nothing is selected, so we can continue
        with contextlib.suppress(DropdownItemDisabled):
            view.searchbar_dropdown.item_select('Select none (0)')

        if select_all_hosts:
            view.searchbox.clear()
            view.select_all.fill(True)
        else:
            if not isinstance(host_names, list):
                host_names = [host_names]
            for host_name in host_names:
                view.search(f'name={host_name}')
                view.table[0][0].widget.fill(True)

        return view

    def change_hosts_owner(self, host_names, new_owner_name, select_all_hosts=False):
        """
        Change owner of selected hosts.

        :param host_names: str with one host or list of hosts to select
        :param new_owner_name: str with new owner name
        :param select_all_hosts: bool, if True, all hosts will be selected
        """

        view = self.all_hosts_navigate_and_select_hosts_helper(host_names, select_all_hosts)

        view.bulk_actions_kebab.click()
        self.browser.move_to_element(view.bulk_actions_menu.item_element('Change associations'))
        view.bulk_actions_change_associations_menu.item_select('Owner')

        view = ChangeHostsOwnerModal(self.browser)
        view.owner_select.item_select(new_owner_name)
        view.confirm_btn.click()

    def change_associations_organization(
        self,
        host_names=None,
        new_organization=None,
        select_all_hosts=False,
        option='Fix on mismatch',
    ):
        """
        Navigate to change organization modal after selecting number of hosts,
        select desired organization, select one of the options and apply changes.

        :param host_names: str with one host or list of hosts to select
        :param new_organization: str organization name which will be selected
        :param select_all_hosts: bool select all hosts flag
        :param option: str options either 'Fix on mismatch' or 'Fail on mismatch'
        """

        if new_organization is None:
            raise ValueError('new_organization argument is None, it will not allow to Save changes')

        view = self.all_hosts_navigate_and_select_hosts_helper(host_names, select_all_hosts)

        view.bulk_actions_kebab.click()
        self.browser.move_to_element(view.bulk_actions_menu.item_element('Change associations'))
        view.bulk_actions_change_associations_menu.item_select('Organization')

        view = ChangeOrganizationModal(self.browser)
        view.organization_menu.item_select(new_organization)

        if option == 'Fix on mismatch':
            view.organization_fix_on_mismatch.fill(True)
            view.save_button.click()

        elif option == 'Fail on mismatch':
            view.organization_fail_on_mismatch.fill(True)
            view.save_button.click()

    def change_associations_location(
        self, host_names=None, new_location=None, select_all_hosts=False, option='Fix on mismatch'
    ):
        """
        Navigate to change location modal after selecting number of hosts,
        select desired location, select one of the options and apply changes.

        :param host_names: str with one host or list of hosts to select
        :param new_location: str location name which will be selected
        :param select_all_hosts: select all hosts flag
        :param option: str options either 'Fix on mismatch' or 'Fail on mismatch'
        """

        if new_location is None:
            raise ValueError('new_location argument is None, it will not allow to Save changes')

        view = self.all_hosts_navigate_and_select_hosts_helper(host_names, select_all_hosts)

        view.bulk_actions_kebab.click()
        self.browser.move_to_element(view.bulk_actions_menu.item_element('Change associations'))
        view.bulk_actions_change_associations_menu.item_select('Location')

        view = ChangeLocationModal(self.browser)
        view.location_menu.item_select(new_location)

        if option == 'Fix on mismatch':
            view.location_fix_on_mismatch.fill(True)
            view.save_button.click()

        elif option == 'Fail on mismatch':
            view.location_fail_on_mismatch.fill(True)
            view.save_button.click()
        else:
            raise ValueError(
                'Option argument is not valid! (fill in "Fix on mismatch" or "Fail on mismatch")'
            )

    def change_associations_host_collections(
        self, host_names=None, select_all_hosts=False, host_collections_to_select=None, option='Add'
    ):
        """
        Navigate to change host collections modal after selecting number of hosts,
        select if user wants to add or remove host collections,
        select desired host collections and apply changes.

        :param host_names: str with one host or list of hosts to select
        :param select_all_hosts: select all hosts flag
        :param host_collections_to_select: str with one host collection or list of host collections to select
        :param option: str options either 'Add' or 'Remove'

        :return: str alert message text, Host collection has reached its limit message or None if no alert message is displayed
        """

        if host_collections_to_select is None:
            raise ValueError(
                'host_collections_to_select argument is None! Please provide host collection(s) to select!'
            )

        view = self.all_hosts_navigate_and_select_hosts_helper(host_names, select_all_hosts)

        view.bulk_actions_kebab.click()
        self.browser.move_to_element(view.bulk_actions_menu.item_element('Change associations'))
        view.bulk_actions_change_associations_menu.item_select('Host collections')

        view = ChangeHostCollectionsModal(self.browser)

        if option == 'Add':
            view.add_to_host_collections_radio.fill(True)
        elif option == 'Remove':
            view.remove_from_host_collections_radio.fill(True)
        else:
            raise ValueError('Option argument is not valid! (fill in "Add" or "Remove")')

        if not isinstance(host_collections_to_select, list):
            host_collections_to_select = [host_collections_to_select]
        for host_collection in host_collections_to_select:
            view.search_input.fill(host_collection)
            wait_for(lambda: view.table.is_displayed, timeout=10)
            if view.table[0][0].widget.is_enabled:
                view.table[0][0].widget.fill(True)
            else:
                view.close_btn.click()
                return (
                    'Failed to add host to host collection. Host collection has reached its limit.'
                )

        view.save_btn.click()

        # Instantiate All Hosts view to access the alert message (without navigation)
        all_hosts_view = AllHostsTableView(self.browser)

        # Wait for and read the alert message
        self.browser.wait_for_element(all_hosts_view.alert_message, exception=False, timeout=5)
        if all_hosts_view.alert_message.is_displayed:
            alert_message_content = all_hosts_view.alert_message.read()
            all_hosts_view.flash.dismiss()
            if 'failed' in alert_message_content.lower():
                view.close_btn.click()
            return alert_message_content
        return None

    def read_host_status_icon(self, host_name):
        """
        Read the status icon details of a specific host.

        :param host_name: str with the name of the host to read the status icon for

        :return: dict with keys 'status' and 'status_details'
        """

        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='5s')
        view.wait_displayed()
        view.search(f'name={host_name}')

        # Find the status icon directly from the Name column cell
        name_cell_element = view.table[0]['Name'].__element__()
        status_button_element = self.browser.element(
            './/button[contains(@class, "pf-v5-c-button")]', parent=name_cell_element
        )

        # Get the span.pf-v5-c-icon element which contains the color style
        icon_span_element = self.browser.element(
            './/span[@class="pf-v5-c-icon"]', parent=status_button_element
        )

        # Get the status of the icon from the style attribute
        icon_style = icon_span_element.get_attribute('style')
        # Extract status from style (e.g., "color: var(--pf-v5-global--success-color--100);")
        possible_statuses = ['success', 'danger', 'warning']
        icon_status = None

        for possible_status in possible_statuses:
            if possible_status in icon_style:
                icon_status = possible_status
                break

        # Click on the status button to open the popover
        status_button_element.click()
        self.browser.wait_for_element(view.popover_body, exception=False, timeout=5)

        status_details = view.popover_body.read()

        view.popover_close_button.click()

        return {'status': icon_status, 'status_details': status_details}

    def read_power_state_icon(self, host_name):
        """
        Read the power state icon details of a specific host.

        :param host_name: str with the name of the host to read the power state icon for

        :return: Power state of host(On, Off)
        """

        view = self.navigate_to(self, 'All')
        self.browser.plugin.ensure_page_safe(timeout='20s')
        view.wait_displayed()
        # Use searchbox directly to avoid calling table.read()
        view.searchbox.search(f'name={host_name}')
        self.browser.plugin.ensure_page_safe(timeout='20s')
        view.table.wait_displayed()

        # Find the status icon directly from the Name column cell
        name_cell_element = view.table[0]['Power'].__element__()
        status_button_element = self.browser.element(
            '//td[@data-label="Power"]//span[@title]', parent=name_cell_element
        )

        # Get the status of the icon from the style attribute
        icon_state = status_button_element.get_attribute('title')
        return {'state': icon_state}

    def manage_traces(
        self,
        host_names=None,
        select_all_hosts=False,
        traces_to_select=None,
    ):
        """
        This function allows to manage traces for selected hosts through the All Hosts page.

        :param host_names: str with one host or list of hosts to select
        :param select_all_hosts: bool, if True, all hosts will be selected
        :param traces_to_select: str with one trace or list of traces to select
        """
        if traces_to_select is None:
            raise ValueError('traces_to_select argument is None! Please provide traces to select!')

        view = self.all_hosts_navigate_and_select_hosts_helper(host_names, select_all_hosts)

        view.bulk_actions_kebab.click()
        view.bulk_actions_menu.item_select('Manage traces')

        view = ManageTracesModal(self.browser)

        if not isinstance(traces_to_select, list):
            traces_to_select = [traces_to_select]
        for trace in traces_to_select:
            view.search_input.fill(f'application="{trace}"')
            wait_for(lambda: view.table.is_displayed, timeout=10)
            row_count = view.table.row_count
            if row_count == 1:
                view.table[0][0].widget.fill(True)
            else:
                # Select page
                view.searchbar_dropdown.item_select(view.searchbar_dropdown.items[-2])

        view.restart_btn.click()

        # Instantiate All Hosts view to access the toast alert (without navigation)
        all_hosts_view = AllHostsTableView(self.browser)

        # Wait for and read the toast alert message
        self.browser.wait_for_element(all_hosts_view.alert_message, exception=False, timeout=5)
        if all_hosts_view.alert_message.is_displayed:
            alert_message_content = all_hosts_view.alert_message.read()
            all_hosts_view.flash.dismiss()
            return alert_message_content
        return None

    def manage_system_purpose(
        self,
        host_names=None,
        select_all_hosts=False,
        role=None,
        usage=None,
        service_level=None,
        release_version=None,
    ):
        """
        This function allows changing system purpose attributes for selected hosts
        through the All Hosts page.

        :param host_names: str with one host or list of hosts to select
        :param select_all_hosts: bool, if True, all hosts will be selected
        :param role: str, system purpose role (e.g., 'Red Hat Enterprise Linux Server')
                     Use 'No change' to keep current values (this is the default in the UI)
                     Use '(unset)' to explicitly unset the value
        :param usage: str, system purpose usage (e.g., 'Production', 'Development/Test')
                      Use 'No change' to keep current values (this is the default in the UI)
                      Use '(unset)' to explicitly unset the value
        :param service_level: str, service level agreement (e.g., 'Premium', 'Standard')
                             Use 'No change' to keep current values (this is the default in the UI)
                             Use '(unset)' to explicitly unset the value
        :param release_version: str, release version
                               Use 'No change' to keep current values (this is the default in the UI)
                               Use '(unset)' to explicitly unset the value
        :return: str, alert message content or None
        """
        view = self.all_hosts_navigate_and_select_hosts_helper(host_names, select_all_hosts)

        view.bulk_actions_kebab.click()
        self.browser.move_to_element(view.bulk_actions_menu.item_element('Manage content'))
        view.bulk_actions_manage_content_menu.item_select('System purpose')

        view = ManageSystemPurposeModal(self.browser)

        # Fill system purpose fields
        fields_to_fill = {}
        if role is not None:
            fields_to_fill['role_select'] = role
        if usage is not None:
            fields_to_fill['usage_select'] = usage
        if service_level is not None:
            fields_to_fill['sla_select'] = service_level
        if release_version is not None:
            fields_to_fill['release_select'] = release_version

        if fields_to_fill:
            view.fill(fields_to_fill)

        view.save_btn.click()

        # Instantiate All Hosts view to access the toast alert (without navigation)
        all_hosts_view = AllHostsTableView(self.browser)

        # Wait for and read the toast alert message
        self.browser.wait_for_element(all_hosts_view.alert_message, exception=False, timeout=5)
        if all_hosts_view.alert_message.is_displayed:
            alert_message_content = all_hosts_view.alert_message.read()
            all_hosts_view.flash.dismiss()
            return alert_message_content
        return None

    def export(self):
        """Export hosts list.

        :return str: path to saved file
        """
        view = self.navigate_to(self, 'All')
        view.export.click()
        return self.browser.save_downloaded_file()


@navigator.register(AllHostsEntity, 'All')
class ShowAllHostsScreen(NavigateStep):
    """Navigate to All Hosts screen."""

    VIEW = AllHostsTableView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'All Hosts')
        self.view.wait_displayed()


@navigator.register(AllHostsEntity, 'ManageColumns')
class HostsManageColumns(NavigateStep):
    """Navigate to the Manage columns dialog"""

    VIEW = AllHostsManageColumnsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        """Open the Manage columns dialog"""
        self.parent.manage_columns.click()

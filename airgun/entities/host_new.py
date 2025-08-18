import time

from navmazing import NavigateToSibling
from wait_for import wait_for

from airgun.entities.host import HostEntity
from airgun.navigation import NavigateStep, navigator
from airgun.utils import retry_navigation
from airgun.views.fact import HostFactView
from airgun.views.host import HostsView as LegacyHostsView
from airgun.views.host_new import (
    AllAssignedRolesView,
    EditAnsibleRolesView,
    EditSystemPurposeView,
    EnableTracerView,
    HostsView,
    InstallPackagesView,
    ManageHostCollectionModal,
    ManageHostStatusesView,
    ModuleStreamDialog,
    NewHostDetailsView,
    ParameterDeleteDialog,
    RemediationView,
)
from airgun.views.hostgroup import HostGroupEditView
from airgun.views.job_invocation import JobInvocationCreateView

available_param_types = ['string', 'boolean', 'integer', 'real', 'array', 'hash', 'yaml', 'json']


def navigate_to_edit_view(func):
    def _decorator(self, entity_name=None, role_name=None):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name, role=role_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        view.overview.details.edit.click()
        self.browser.switch_to_window(self.browser.window_handles[1])
        host_group_view = HostGroupEditView(self.browser)
        func(self, entity_name, role_name)
        host_group_view.ansible_roles.submit.click()
        self.browser.switch_to_window(self.browser.window_handles[0])
        self.browser.close_window(self.browser.window_handles[1])

    return _decorator


class NewHostEntity(HostEntity):
    endpoint_path = '/new/hosts'

    def create(self, values):
        """Create new host entity"""
        view = self.navigate_to(self, 'New')
        view.fill(values)
        self.browser.click(view.submit, ignore_ajax=True)
        self.browser.plugin.ensure_page_safe(timeout='600s')
        host_view = NewHostDetailsView(self.browser)
        host_view.wait_displayed()
        host_view.flash.assert_no_error()
        host_view.flash.dismiss()

    def get_details(self, entity_name, widget_names=None):
        """Read host values from Host Details page, optionally only the widgets in widget_names
        will be read.
        """
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.read(widget_names=widget_names)

    def run_bootc_job(self, entity_name, job_name, job_options=None):
        """Navigate to the Host Details UI, and run a specified job from the link on the bootc card."""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        view.details.bootc.remote_execution_link.click()
        if job_options:
            job_input = {
                'target_hosts_and_inputs.action': f'{job_name}',
                'target_hosts_and_inputs.options': f'{job_options}',
            }
        else:
            job_input = {'target_hosts_and_inputs.action': f'{job_name}'}
        view = JobInvocationCreateView(self.browser)
        view.fill(job_input)
        view.submit.click()

    @navigate_to_edit_view
    def assign_role_to_hostgroup(self, entity_name, role_name):
        """Assign a single Ansible role from the host group based on user input

        Args:
            entity_name: Name of the host
            role_name: Name of the ansible role
        """
        host_group_view = HostGroupEditView(self.browser)
        host_group_view.ansible_roles.more_item.click()
        host_group_view.ansible_roles.select_pages.click()
        role_list = self.browser.elements(host_group_view.ansible_roles.available_role, parent=self)
        for single_role in role_list[1:]:
            if single_role.text.split(". ")[1] == role_name:
                single_role.click()

    @navigate_to_edit_view
    def remove_hostgroup_role(self, entity_name, role_name):
        """Remove a single Ansible role from the host group based on user input

        Args:
            entity_name: Name of the host
            role_name: Name of the ansible role
        """
        host_group_view = HostGroupEditView(self.browser)
        role_list = self.browser.elements(host_group_view.ansible_roles.assigned_role, parent=self)
        for single_role in role_list[1:]:
            if single_role.text.split(". ")[1] == role_name:
                single_role.click()

    @navigate_to_edit_view
    def assign_all_role_to_hostgroup(self, entity_name, role_name=None):
        """Assign all Ansible roles from the host group"""
        host_group_view = HostGroupEditView(self.browser)
        host_group_view.ansible_roles.more_item.click()
        host_group_view.ansible_roles.select_pages.click()
        role_list = self.browser.elements(host_group_view.ansible_roles.available_role, parent=self)
        for single_role in role_list:
            single_role.click()

    @navigate_to_edit_view
    def remove_all_role_from_hostgroup(self, entity_name, role_name=None):
        """Remove all Ansible roles from the host group"""
        host_group_view = HostGroupEditView(self.browser)
        host_group_view.ansible_roles.click()
        role_list = self.browser.elements(host_group_view.ansible_roles.assigned_role, parent=self)
        for single_role in role_list:
            single_role.click()

    def get_host_statuses(self, entity_name):
        """Read host statuses from Host Details page

        Args:
            entity_name: Name of the host
        """
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        view.overview.host_status.manage_all_statuses.click()
        view = ManageHostStatusesView(self.browser)
        values = view.read()
        view.close_modal.click()
        return values

    def edit_system_purpose(
        self, entity_name, role=None, sla=None, usage=None, release_ver=None, add_ons=None
    ):
        """
        Function that edits the system purpose of a host

        Args:
            entity_name: Name of the host
            role: Role to be assigned
            sla: SLA to be assigned
            usage: Usage to be assigned
            release_ver: Release version to be assigned
            add_ons: Add-ons to be assigned

        Raises:
            ValueError: If no parameters are passed.
        """

        if not any([role, sla, usage, release_ver, add_ons]):
            raise ValueError(
                'At least one of the role, sla, usage, release_ver, add_ons must be provided!'
            )
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        view.overview.system_purpose.edit_system_purpose.click()
        view = EditSystemPurposeView(self.browser)
        self.browser.plugin.ensure_page_safe()
        view.wait_displayed()
        if role:
            view.role.fill(role)
        if sla:
            view.sla.fill(sla)
        if usage:
            view.usage.fill(usage)
        if release_ver:
            view.release_version.fill(release_ver)
        if add_ons:
            view.add_ons.fill(add_ons)
        view.save.click()

    def add_host_to_host_collection(
        self, entity_name, host_collection_name=None, add_to_all_collections=False
    ):
        """
        Function that adds host to host collection

        Args:
            entity_name: Name of the host
            host_collection_name: Name  or list of the host collection we want to add the host to
            add_to_all_collections: If True, host will be added to all host collections

        Raises:
            ValueError: If specific hostColName is set to be removed and add all is set to True
                        or if no parameters are passed.
            ValueError: If host is already assigned to selected host collection.
            ValueError: If there is empty list provided for host_collection_name.
            ValueError: If there are no host collections left for addition.
            ValueError: Given host collection name is not found in host collections.
        """

        if (host_collection_name and add_to_all_collections) or (
            (host_collection_name is None) and (add_to_all_collections is False)
        ):
            raise ValueError(
                'Either host_collection_name or add_to_all_collections must be provided!'
            )

        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        # Handle the case where there are no host collections assigned
        if view.overview.host_collections.no_host_collections.is_displayed:
            view.overview.host_collections.add_to_host_collection.click()
        else:
            if (
                host_collection_name
                in view.overview.host_collections.assigned_host_collections.read()
            ):
                raise ValueError(f'{host_collection_name} already assigned to host!')
            view.overview.host_collections.kebab_menu.item_select('Add host to collections')

        view = ManageHostCollectionModal(self.browser)
        self.browser.plugin.ensure_page_safe()
        view.wait_displayed()

        if view.create_host_collection.is_displayed:
            raise ValueError('No host collections found or left for addition!')

        if not add_to_all_collections:
            if isinstance(host_collection_name, list):
                if not host_collection_name:
                    raise ValueError('host_collection_name list is empty!')
                for host_col in host_collection_name:
                    view.searchbar.fill("name = " + host_col, enter_timeout=2)
                    view.wait_displayed()
                    self.browser.plugin.ensure_page_safe()
                    if view.host_collection_table.row_count == 0:
                        raise ValueError(f'{host_col} not found in host collections!')
                    time.sleep(3)
                    # Select the host collection via checkbox in the table
                    view.host_collection_table[0][0].widget.click()
            else:
                view.searchbar.fill("name = " + host_collection_name, enter_timeout=2)
                view.wait_displayed()
                self.browser.plugin.ensure_page_safe()
                if view.host_collection_table.row_count == 0:
                    raise ValueError(f'{host_collection_name} not found in host collections!')
                time.sleep(3)
                # Select the host collection via checkbox in the table
                view.host_collection_table[0][0].widget.click()
        else:
            view.select_all.click()
        view.add.click()

    def remove_host_from_host_collection(
        self, entity_name, host_collection_name=None, remove_from_all_collections=False
    ):
        """
        Function that removes host from host collection

        Args:
            entity_name: Name of the host
            host_collection_name: Name or list of the host collection we want to remove host from
            remove_from_all_collections: If True, host will be removed from all host collections

        Raises:
            ValueError: If specific hostColName is set to be removed & remove all is set to True
                            or if no parameters are passed.
            ValueError: If host is not assigned to any host collection.
            ValueError: If there is empty list provided for host_collection_name.
            ValueError: If given host col name we want to remove is not assigned to host.
        """

        if ((host_collection_name is not None) and remove_from_all_collections) or (
            (host_collection_name is None) and (remove_from_all_collections is False)
        ):
            raise ValueError(
                'Either host_collection_name or add_to_all_collections must be provided!'
            )

        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        # Handle the case where there are no host collections assigned
        view.overview.click()
        if view.overview.host_collections.no_host_collections.is_displayed:
            raise ValueError('No host collections assigned to host, thus nothing to remove!')

        view.overview.host_collections.kebab_menu.item_select('Remove host from collections')
        view = ManageHostCollectionModal(self.browser)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()

        if not remove_from_all_collections:
            if isinstance(host_collection_name, list):
                if not host_collection_name:
                    raise ValueError('host_collection_name list is empty!')
                for host_col in host_collection_name:
                    view.searchbar.fill("name = " + host_col, enter_timeout=2)
                    view.wait_displayed()
                    self.browser.plugin.ensure_page_safe()
                    if not view.host_collection_table.is_displayed:
                        raise ValueError(f"{host_col} not assigned to host, thus can't remove it!")
                    time.sleep(3)
                    # Select the host collection via checkbox in the table
                    view.host_collection_table[0][0].widget.click()
            else:
                view.searchbar.fill("name = " + host_collection_name, enter_timeout=2)
                view.wait_displayed()
                self.browser.plugin.ensure_page_safe()
                if not view.host_collection_table.is_displayed:
                    raise ValueError(
                        f"{host_collection_name} not assigned to host, thus can't remove it!"
                    )
                time.sleep(3)
                # Select the host collection via checkbox in the table
                view.host_collection_table[0][0].widget.click()
        else:
            view.select_all.click()
        view.remove.click()

    def schedule_job(self, entity_name, values):
        """Schedule a remote execution on selected host"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        self.browser.plugin.ensure_page_safe()
        view.wait_displayed()
        self.browser.wait_for_element(view.schedule_job, exception=False)
        view.schedule_job.fill('Schedule a job')
        view = JobInvocationCreateView(self.browser)
        self.browser.plugin.ensure_page_safe()
        view.fill(values)
        view.submit.click()

    def run_job(self, entity_name):
        """Run a job on selected host"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.run_job.wait_displayed()
        view.run_job.click()
        view.select.click()

    def get_packages(self, entity_name, search=""):
        """Filter installed packages on host"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.content.packages.wait_displayed()
        view.content.packages.select()
        wait_for(lambda: view.content.packages.table.is_displayed, timeout=5)
        view.content.packages.searchbar.fill(search)
        self.browser.plugin.ensure_page_safe()
        # Check if there is a match
        if view.content.packages.no_matching_packages.is_displayed:
            return None
        else:
            view.content.packages.table.wait_displayed()
            return view.content.packages.table.read()

    def install_package(self, entity_name, package):
        """Installs package on host using the installation modal"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        view.content.packages.select()
        view.content.packages.dropdown.wait_displayed()
        view.content.packages.dropdown.item_select('Install packages')
        view = InstallPackagesView(self.browser)
        view.wait_displayed()
        view.searchbar.fill(package)
        # wait for filter to apply
        self.browser.plugin.ensure_page_safe()
        view.table[0][0].widget.fill(True)
        view.install.click()

    def apply_package_action(self, entity_name, package_name, action):
        """Apply `action` to selected package based on the `package_name`"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        view.content.packages.searchbar.fill(package_name)
        # wait for filter to apply
        self.browser.plugin.ensure_page_safe()
        view.content.packages.table.wait_displayed()
        view.content.packages.table[0][5].widget.item_select(action)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def get_errata_table(
        self,
        entity_name,
        installable=None,
        severity=None,
        search=None,
        type=None,
    ):
        """Return the table of all errata entries, from Errata tab on selected host.
        param: entity_name str: hostname to search for errata table

        Optional: Filter by passing args (string):
            param: installable str: filter errata by installability ('Yes' or 'No').
            param: severity str: filter errata by severity.
            param: search str: pass a search query to the searchbar, prior to reading.
            param: type str: filter errata search by type.

        note: all of the optional params being None, will result in no filtering.
        """
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        view.content.errata.select()
        # optional: filter by params that are not None
        if installable is not None:
            assert installable == 'Yes' or 'No', (
                'installable_filter expected None or str, "Yes" or "No".'
                f' Got: {installable}, ({type(installable)}).'
            )
            view.content.errata.installable_filter.fill(installable)
        if type is not None:
            view.content.errata.type_filter.fill(type)
        if severity is not None:
            view.content.errata.severity_filter.fill(severity)
        if search is not None:
            view.content.errata.searchbar.fill(search)
        # displayed the table with or without filters
        view.content.errata.table.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.content.errata.table.read()

    def get_errata_by_type(self, entity_name, type):
        """List errata based on type and return table"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        view.content.errata.select()
        view.content.errata.type_filter.fill(type)
        self.browser.plugin.ensure_page_safe()
        view.content.errata.table.wait_displayed()
        return view.read(widget_names="content.errata.table")

    def get_errata_type_counts(self, entity_name):
        """
        Get errata counts for each type of errata on selected host.

        Args:
            entity_name: Name of the host.
        Returns:
            errata_counts (dict): Dictionary with counts of each type of errata.
        """

        errata_types = ['Security', 'Bugfix', 'Enhancement']
        errata_counts = dict.fromkeys(errata_types, 0)
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        view.content.errata.select()
        for type in errata_types:
            view.content.errata.wait_displayed()
            view.content.errata.pagination.set_per_page(50)
            view.content.errata.type_filter.fill(type)
            self.browser.plugin.ensure_page_safe()
            view.content.errata.table.wait_displayed()
            errata_counts[type] = view.content.errata.table.row_count
        return errata_counts

    def apply_erratas(self, entity_name, search=None):
        """Apply available errata on selected host based on searchbar result.

        param: search (string): search value to filter results.
        example: search="errata_id == {ERRATA_ID}"
        default: None; all available errata are returned and installed.
        """
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        if search is None:
            # Return all errata, clear the searchbar
            view.content.errata.searchbar.clear()
        else:
            # Return only errata by search
            view.content.errata.searchbar.fill(search)
        # wait for filter to apply
        view.content.errata.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        view.content.errata.select_all.click()
        view.content.errata.apply.fill('Apply')
        view.flash.assert_no_error()
        view.flash.dismiss()
        # clear the searchbar so any input will not persist
        view.content.errata.searchbar.clear()
        view.content.errata.wait_displayed()
        self.browser.plugin.ensure_page_safe()

    def get_errata_pagination(self, entity_name):
        """Get pagination info from Errata tab on selected host."""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        view.content.errata.select()
        view.content.errata.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.content.errata.pagination

    def get_module_streams(self, entity_name, search):
        """Filter module streams"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        view.content.module_streams.select()
        view.content.module_streams.searchbar.fill(search)
        # wait for filter to apply
        self.browser.wait_for_element(locator='//h4[text()="Loading"]', exception=False)
        view.content.module_streams.table.wait_displayed()
        return view.content.module_streams.table.read()

    def apply_module_streams_action(self, entity_name, module_stream, action):
        """Apply `action` to selected Module stream based on the `module_stream`"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        view.content.module_streams.searchbar.fill(module_stream)
        # wait for filter to apply
        self.browser.plugin.ensure_page_safe()
        view.content.module_streams.table[0][5].widget.item_select(action)
        modal = ModuleStreamDialog(self.browser)
        if modal.is_displayed:
            modal.confirm()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def get_repo_sets(self, entity_name, search):
        """Get all repository sets available for host"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        view.content.repository_sets.searchbar.fill(search)
        self.browser.plugin.ensure_page_safe()
        time.sleep(3)
        return view.content.repository_sets.table.read()

    def override_repo_sets(self, entity_name, repo_set, action):
        """Change override for repository set"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        view.content.repository_sets.searchbar.fill(repo_set)
        self.browser.plugin.ensure_page_safe()
        view.content.repository_sets.table[0][6].widget.click()
        view.content.repository_sets.repo_set_action.item_select(action)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def override_multiple_repo_sets(self, entity_name, repo_set, repo_type, action):
        """Change override for multiple repository sets without using the Select All method"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        view.content.repository_sets.searchbar.fill(repo_set)
        view.content.repository_sets.table[0][0].widget.click()
        view.content.repository_sets.dropdown.item_select(action)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def bulk_override_repo_sets(self, entity_name, repo_type, action):
        """Change override for repository set"""
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        view.content.repository_sets.repository_type.item_select(repo_type)
        view.content.repository_sets.select_all.click()
        view.content.repository_sets.dropdown.item_select(action)
        view.flash.assert_no_error()
        view.flash.dismiss()

    def add_single_ansible_role(self, entity_name, role=None):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        wait_for(lambda: view.ansible.roles.edit.is_displayed, timeout=5)
        view.ansible.roles.edit.click()
        wait_for(lambda: EditAnsibleRolesView(self.browser).addAnsibleRole.is_displayed, timeout=10)
        edit_view = EditAnsibleRolesView(self.browser)
        edit_view.addAnsibleRole.select_and_move([role])
        edit_view.confirm.click()

    def get_ansible_roles(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        wait_for(lambda: view.ansible.roles.table.is_displayed, timeout=5)
        return view.ansible.roles.table.read()

    def get_ansible_roles_modal(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        view.ansible.roles.assignedRoles.click()
        view = AllAssignedRolesView(self.browser)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.table.read()

    def remove_single_ansible_role(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        view.ansible.roles.edit.click()
        wait_for(lambda: view.ansible.roles.edit.click(), timeout=5)
        edit_view = EditAnsibleRolesView(self.browser)
        edit_view.wait_displayed()
        actions = [edit_view.hostAssignedAnsibleRoles, edit_view.unselectRoles, edit_view.confirm]
        for action in actions:
            action.click()
        wait_for(lambda: view.ansible.roles.noRoleAssign.is_displayed, timeout=5)

    def enable_tracer(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        view.traces.enable_traces.click()
        modal = EnableTracerView(self.browser)
        if modal.is_displayed:
            modal.confirm.click()
        view.flash.assert_no_error()
        view.flash.dismiss()

    def get_tracer(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.traces.read()

    def get_tracer_tab_title(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        view.traces.click()
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.traces.title.text

    def get_os_info(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.details.operating_system.read()

    def get_provisioning_info(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.details.provisioning.read()

    def get_bios_info(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.details.bios.read()

    def get_registration_details(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.details.registration_details.read()

    def get_hw_properties(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.details.hw_properties.read()

    def get_provisioning_templates(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        d = view.details.read()
        return d['provisioning_templates']['templates_table']

    def get_networking_interfaces(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.details.networking_interfaces.networking_interfaces_accordion.items()

    def get_networking_interfaces_details(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        net_devices = [
            i.split()[0]
            for i in view.details.networking_interfaces.networking_interfaces_accordion.items()
        ]

        for dev in net_devices[1:]:
            view.details.networking_interfaces.networking_interfaces_accordion.toggle(dev)

        def dict_val_gen(item_name):
            """Generator needed to fill the networking interface dictionary"""
            locator_templ = (
                './/div[contains(@class, "pf-c-accordion__expanded-content-body")]'
                '//div[.//dt[normalize-space(.)="{}"]]//div'
            )
            values = self.browser.elements(locator_templ.format(item_name))
            yield values

        networking_interface_dict = {}
        tmp = {
            'fqdn': [i.text for i in next(iter(dict_val_gen('FQDN')))],
            'ipv4': [i.text for i in next(iter(dict_val_gen('IPv4')))],
            'ipv6': [i.text for i in next(iter(dict_val_gen('IPv6')))],
            'mac': [i.text for i in next(iter(dict_val_gen('MAC')))],
            # TODO: After RFE BZ2183086 is resolved, uncomment line below
            # 'subnet': [i.text for i in list(dict_val_gen('Subnet'))[0]],
            'mtu': [i.text for i in next(iter(dict_val_gen('MTU')))],
        }

        for i, dev in enumerate(net_devices):
            networking_interface_dict[dev] = {key: tmp[key][i] for key in tmp}

        return networking_interface_dict

    def get_installed_products(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        installed_products_list = view.details.installed_products.read()
        return installed_products_list['installed_products_list']

    def get_parameters(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.parameters.read()

    def get_virtualization(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.details.virtualization.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.details.virtualization.read()

    def add_new_parameter(self, entity_name, parameter_name, parameter_type, parameter_value):
        """
        Function that adds new parameter to the host

        Args:
            entity_name: host on which we want to add parameter
            parameter_name: Name of the parameter to be added
            parameter_type: Type of the parameter to be added
                [string, boolean, integer, real, array, hash, yaml, json]
            parameter_value: Value of the parameter to be added

        Raises:
            ValueError: If parameter type is not valid
            ValueError: If parameter with the same name already exists
        """

        # Sanitize input
        parameter_type = parameter_type.lower()
        if parameter_type not in available_param_types:
            raise ValueError(
                f'Parameter type {parameter_type} is not valid!'
                f'Available types are: {available_param_types}'
            )

        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        view.parameters.click()
        view.parameters.table_header.sort_by('name', 'ascending')
        view.parameters.searchbar.fill(parameter_name)
        view.wait_displayed()
        # Check if parameter with given name does not exist. If it does, raise ValueError.
        if view.parameters.parameters_table.row_count != 0:
            if view.parameters.parameters_table[0][0].text == parameter_name:
                raise ValueError(f'Parameter with name {parameter_name} already exists!')

        view.parameters.add_parameter.click()
        view.parameters.parameter_name_input.fill(parameter_name)
        view.parameters.parameter_type_input.fill(parameter_type)
        view.parameters.parameter_value_input.fill(parameter_value)
        view.parameters.confirm_addition.click()

    def edit_parameter(
        self,
        entity_name,
        parameter_to_change,
        new_parameter_name=None,
        new_parameter_type=None,
        new_parameter_value=None,
    ):
        """
        Function that can edit parameter name, type or value separetely or all of them at once.

        Args:
            entity_name: Name of the entity to be edited
            parameter_to_change: Name of the parameter to be edited
            new_parameter_name: New name of the parameter
            new_parameter_type: New type of the parameter
                [string, boolean, integer, real, array, hash, yaml, json]
            new_parameter_value: New value of the parameter

        Raises:
            ValueError: No new parameter name, type or value provided
            ValueError: If parameter type is not valid
            ValueError: If parameter_to_change is not found on host
            ValueError: If parameter with new name already exists
        """

        if not any([new_parameter_name, new_parameter_type, new_parameter_value]):
            raise ValueError(
                'At least one of the new_parameter_name, new_parameter_type, new_parameter_value '
                'must be provided!'
            )
        # Sanitize input
        new_parameter_type = new_parameter_type.lower()
        if new_parameter_type not in available_param_types:
            raise ValueError(
                f'Parameter type {new_parameter_type} is not valid!'
                f'Available types are: {available_param_types}'
            )

        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        view.parameters.click()
        view.parameters.table_header.sort_by('name', 'ascending')
        view.parameters.searchbar.fill(parameter_to_change)
        view.wait_displayed()
        if (view.parameters.parameters_table.row_count == 0) or (
            view.parameters.parameters_table[0][0].text != parameter_to_change
        ):
            raise ValueError(
                f'Parameter {parameter_to_change} not found on {entity_name}, '
                'thus cannot be edited.'
            )

        view.parameters.searchbar.fill(new_parameter_name)
        view.wait_displayed()
        if view.parameters.parameters_table.row_count != 0:
            if view.parameters.parameters_table[0][0].text == new_parameter_name:
                raise ValueError(
                    f'Cannot rename {parameter_to_change} to {new_parameter_name}. '
                    'This parameter already exists.'
                )

        view.parameters.searchbar.fill(parameter_to_change)
        view.wait_displayed()
        # Click edit button in the row
        view.parameters.parameters_table[0][4].widget.click()
        view.wait_displayed()
        if new_parameter_name:
            view.parameters.parameter_name_input.fill(new_parameter_name)
        if new_parameter_type:
            view.parameters.parameter_type_input.fill(new_parameter_type)
        if new_parameter_value:
            view.parameters.parameter_value_input.fill(new_parameter_value)
        view.parameters.confirm_addition.click()

    def delete_parameter(self, entity_name, parameter_name):
        """
        Function that deletes parameter from the host

        Args:
            entity_name: Name of the host to be edited
            parameter_name: Name of the parameter to be deleted

        Raises:
            ValueError: If given parameter is not found on host
        """

        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        view.parameters.click()
        view.parameters.searchbar.fill(parameter_name)
        view.wait_displayed()
        # Fail if there are no parameters or if first parameter is not the one we are looking for
        if (view.parameters.parameters_table.row_count == 0) or (
            view.parameters.parameters_table[0][0].text != parameter_name
        ):
            raise ValueError(
                f'Parameter {parameter_name} not found on {entity_name}, thus cannot be deleted.'
            )

        view.parameters.parameters_table[0][5].widget.item_select('Delete')
        delete_modal = ParameterDeleteDialog(self.browser)
        if delete_modal.is_displayed:
            delete_modal.confirm_delete.click()

    def get_traces(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.traces.read()

    def get_puppet_details(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        reports_table = view.puppet.puppet_reports_table.read()
        x = view.puppet.puppet_details.read()
        x['reports_table'] = reports_table
        return x

    def get_puppet_enc_preview(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.puppet.enc_preview.read()

    def get_reports(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.reports.read()

    def get_insights(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        wait_for(lambda: view.insights.recommendations_table.is_displayed, timeout=10)
        return view.insights.read()

    def get_vulnerabilities(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return view.vulnerabilities.vulnerabilities_table.read()

    def remediate_with_insights(
        self, entity_name, recommendation_to_remediate=None, remediate_all=False
    ):
        """
        Function that can remediate all or one recommendation with insights.

        Args:
            entity_name: Name of the host on which recommendations are to be remediated
            recommendation_to_remediate: Name of the recommendation to be remediated
            remediate_all: If True, all recommendations will be remediated

        Raises:
            ValueError: If recommendation_to_remediate is None and remediate_all is False
                    or if both recommendation_to_remediate and remediate_all are provided.
            IndexError: If given recommendation is not found

        """

        if ((recommendation_to_remediate is not None) and remediate_all) or (
            (recommendation_to_remediate is None) and (remediate_all is False)
        ):
            raise ValueError(
                'Either recommendation_to_remediate or remediate_all must be provided!'
            )

        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        if remediate_all:
            view.insights.select_all_one_page.click()
            view.insights.select_all_pages.click()
        else:
            view.insights.recommendations_table.sort_by('Recommendation', 'ascending')

            if isinstance(recommendation_to_remediate, list):
                if not recommendation_to_remediate:
                    raise ValueError('List of recommendations cannot be empty!')
                for recommendation in recommendation_to_remediate:
                    view.insights.click()
                    # Excape double quotes in the recommendation
                    _rec = recommendation.replace('"', '\\"')
                    _rec = f'title = "{_rec}"'
                    view.insights.search_bar.fill(_rec, enter_timeout=3)
                    view.wait_displayed()
                    self.browser.plugin.ensure_page_safe()
                    time.sleep(3)
                    try:
                        # Click the checkbox of the first recommendation
                        view.insights.recommendations_table[0][0].widget.click()
                    except IndexError as ie:
                        raise IndexError(
                            f'Recommendation {_rec} not found on {entity_name}, '
                            'thus cannot be remediated.'
                        ) from ie
            else:
                # Excape double quotes in the recommendation
                recommendation_to_remediate = recommendation_to_remediate.replace('"', '\\"')
                recommendation_to_remediate = f'title = "{recommendation_to_remediate}"'
                view.insights.search_bar.fill(recommendation_to_remediate, enter_timeout=3)
                view.wait_displayed()
                self.browser.plugin.ensure_page_safe()
                time.sleep(3)
                try:
                    # Click the checkbox of the first recommendation
                    view.insights.recommendations_table[0][0].widget.click()
                except IndexError as ie:
                    raise IndexError(
                        f'Recommendation {recommendation_to_remediate} not found '
                        f'on {entity_name}, thus cannot be remediated.'
                    ) from ie
        view.insights.remediate.click()
        view = RemediationView(self.browser)
        view.remediate.click()

    def get_host_facts(self, entity_name, fact=None):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        self.browser.plugin.ensure_page_safe()
        view.wait_displayed()
        self.browser.wait_for_element(view.dropdown, exception=False)
        view.dropdown.item_select('Facts')
        host_facts_view = HostFactView(self.browser)
        if fact:
            host_facts_view.searchbox.search(fact)
            if host_facts_view.expand_fact_value.is_displayed:
                host_facts_view.expand_fact_value.click()
        return host_facts_view.table.read()

    def refresh_applicability(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        view.dropdown.item_select('Refresh applicability')

    def update_variable_value(self, entity_name, key, value):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        wait_for(lambda: view.ansible.variables.table.is_displayed, timeout=10)
        # Index [5] essentially refers to the button used to edit the value. The same index is then applied to either 'Yes' or 'No' options to update the value
        view.ansible.variables.table.row(name=key)[5].widget.click()
        view.ansible.variables.table.row(name=key)['Value'].click()
        view.ansible.variables.table.row(name=key)['Value'].widget.fill(value)
        view.ansible.variables.table1.row(name=key)[5].widget.click()

    def del_variable_value(self, entity_name):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        view.ansible.variables.actions.click()
        view.ansible.variables.delete.click()
        view.ansible.variables.confirm.click()

    def read_variable_value(self, entity_name, key):
        view = self.navigate_to(self, 'NewDetails', entity_name=entity_name)
        value = view.ansible.variables.table.row(name=key)['Value'].read()
        return value

    def show_hosts_legacy_ui(self):
        """Switch to legacy Hosts UI"""
        view = self.navigate_to(self, 'NewUIAll')
        view.actions.item_select('Legacy UI')
        legacy_view = LegacyHostsView(self.browser)
        legacy_view.wait_displayed()
        self.browser.plugin.ensure_page_safe()
        return legacy_view


@navigator.register(HostEntity, 'NewUIAll')
class ShowAllHosts(NavigateStep):
    """Navigate to new UI All Hosts page"""

    VIEW = HostsView

    @retry_navigation
    def step(self, *args, **kwargs):
        self.view.menu.select('Hosts', 'All Hosts')


@navigator.register(NewHostEntity, 'NewDetails')
class ShowNewHostDetails(NavigateStep):
    """Navigate to Host Details page by clicking on necessary host name in the table

    Args:
        entity_name: name of the host
    """

    VIEW = NewHostDetailsView

    def prerequisite(self, *args, **kwargs):
        return self.navigate_to(self.obj, 'All')

    def step(self, *args, **kwargs):
        entity_name = kwargs.get('entity_name')
        self.parent.search(entity_name)
        self.parent.table.row(name=entity_name)['Name'].widget.click()


@navigator.register(NewHostEntity, 'AnsibleTab')
class ShowNewHostAnsible(NavigateStep):
    """Navigate to the Ansible Tab of Host Details by clicking on the subtab"""

    VIEW = NewHostDetailsView

    prerequisite = NavigateToSibling('NewDetails')
